# -*- coding: utf-8 -*-
# Copyright (C) 2016  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Anne Mulhern <amulhern@redhat.com>

"""
    pydevDAG._queries._enclosures
    =============================

    Grouping devices by enclosures.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools

from collections import defaultdict
from collections import namedtuple

from .._attributes import EdgeTypes
from .._attributes import NodeTypes

from .._errors import DAGGraphError

from .._item_str import NodeGetters

from .._utils import Dict
from .._utils import GeneralUtils


_Info = namedtuple('_Info', ['target', 'identifier', 'disk', 'devices'])

class ByEnclosures(object):
    """
    Group devices by enclosure.
    """
    # pylint: disable=too-few-public-methods

    _ENCLOSURE_FUNC = staticmethod(NodeGetters.SYSNAME.getter)
    _TARGET_FUNC = staticmethod(
       GeneralUtils.composer(
           [
              NodeGetters.DMNAME.getter,
              NodeGetters.DEVNAME.getter
           ]
       )
    )
    _DEVICES_FUNC = staticmethod(NodeGetters.DEVNAME.getter)

    @staticmethod
    def _get_devices_for_enclosure(graph, enclosure):
        """
        Get devices for ``enclosure``.

        :param DiGraph graph: the graph
        :param str enclosure: the enclosure device

        :raises DAGGraphError: if the graph is unexpected

        Yields a sequence of _Info objects.
        """
        for (_, target, data) in graph.out_edges_iter(enclosure, data=True):
            if data['edgetype'] is not EdgeTypes.ENCLOSUREBAY:
                continue
            identifier = data.get('identifier')
            if identifier is None:
                raise DAGGraphError('enclosure bay edge has no identifier')
            disks = [
               t for (_, t, d) in graph.out_edges_iter(target, data=True) if \
                  d['edgetype'] is EdgeTypes.SPINDLE
            ]
            if len(disks) != 1:
                raise DAGGraphError('should be only one device -> disk edge')
            yield _Info(target, identifier, disks[0], [])

    @staticmethod
    def _get_enclosure_devices(graph):
        """
        Get all enclosure devices in the graph.

        :param DiGraph graph: the graph

        Yields a sequence of enclosure devices.
        """
        for node, attrs in graph.nodes_iter(data=True):
            if attrs['nodetype'] == NodeTypes.DEVICE_PATH and \
               Dict.get_value(attrs, ['UDEV', 'SUBSYSTEM']) == 'enclosure':
                yield node

    @staticmethod
    def _group_enclosures(enclosure_infos):
        """
        Group enclosures in tuples according to the disks they refer to.

        :param enclosure_infos: enclosure/info pairs.
        :type enclosure_infos: dict of str * _Info
        :returns: a map of sets of enclosure names to sets of disk ids
        :rtype: dict of (set of str) * (set of str)

        Note that if an enclosure device has an empty set of disks it is
        ignored, as otherwise it would be grouped with any other enclosures
        that have an empty set of disks, which would be meaningless for
        giving an actual identity to the enclosure device.
        """
        enclosure_spindles = (
           (e, frozenset(x.disk for x in devs)) \
              for (e, devs) in enclosure_infos.items()
        )

        spindle_set_map = defaultdict(list)
        for (enc, dset) in enclosure_spindles:
            if len(dset) != 0:
                spindle_set_map[dset].append(enc)

        return dict(
           (frozenset(enc), dset) for (dset, enc) in spindle_set_map.items()
        )

    @staticmethod
    def _find_enclosure_subsets(enclosure_sets):
        """
        Find any propert subset relationships.

        :param enclosure_sets: a sequence of enclosure sets
        :type enclosure_sets: a sequence of sets of enclosure identifiers

        :returns: a map from super to subset
        :rtype: dict of set * set

        Assumes that all sets are either disjoint or have a subset relationship.
        In other words, if x & y is not empty, then x < y or y < x.
        """
        subsets = dict()
        sorted_sets = sorted(enclosure_sets, key=len)
        for (index, encs) in enumerate(sorted_sets):
            sset = next(
               (t for t in sorted_sets[(index + 1):] if encs < t),
               None
            )
            if sset is not None:
                subsets[encs] = sset

        return subsets

    @staticmethod
    def _get_dm_device(graph, device):
        """
        Get the parent dm device for ``device``.

        :param DiGraph graph: the graph
        :param str device: the device

        :returns: the dm holder for this device if any
        :rtype: str or NoneType
        """
        for (source, _, data) in graph.in_edges_iter(device, data=True):
            if data['edgetype'] is EdgeTypes.SLAVE:
                dm_uuid = \
                   Dict.get_value(graph.node[source], ['UDEV', 'DM_UUID'])
                if dm_uuid is not None:
                    return source
        return None

    @classmethod
    def _get_shared_dm_device(cls, graph, devices):
        """
        Get the shared parent dm device for ``devices``.

        :param DiGraph graph: the graph
        :param devices: a sequence of devices
        :type devices: elements of type str

        :returns: mpath device or None if none found
        :rtype: str or NoneType
        """
        dms = list(
           frozenset(cls._get_dm_device(graph, dev) for dev in devices)
        )
        if len(dms) == 1:
            return dms[0]
        else:
            return None

    @classmethod
    def _combine_enclosure_info(cls, graph, enclosure_map, spindle_map):
        """
        Get a new map where the keys are those from ``spindle_map`` and the
        values are combined _Infos from ``enclosure_map`` including the
        relevant device.

        :param DiGraph graph: the graph
        :param enclosure_map: map from enclosure device to info
        :type enclosure_map: dict of str * (list of _Info)
        :param spindle_map: map from enclosure sets to sets of spindles
        :type spindle_map: dict of (set of str) * (set of str)

        :returns: map of enclosure sets to lists of device information
        :rtype: dict of (sorted list of str) * (list of _Info)

        :raises DAGGraphError: if graph is malformed

        _Info object's target attribute is a pair of the unique device,
        which may be multipath, and of its component devices, if any.
        """
        sort_func = lambda x: x.identifier

        result = defaultdict(list)
        for encs in spindle_map.keys():
            infos = itertools.groupby(
               sorted(
                  (i for enc in encs for i in enclosure_map[enc]),
                  key=sort_func
               ),
               sort_func
            )
            for (identifier, id_info) in infos:
                info_list = list(id_info)

                disks = set(i.disk for i in info_list)
                if len(disks) != 1:
                    raise DAGGraphError('more than one disk per enclosure slot')

                devices = list(set(i.target for i in info_list))
                mpath = cls._get_shared_dm_device(graph, devices)

                if mpath is not None:
                    target = mpath
                elif len(devices) == 1 and len(encs) == 1:
                    target = devices[0]
                    devices = []
                else:
                    target = False

                result[encs].append(
                   _Info(target, identifier, list(disks)[0], sorted(devices))
                )

        return result

    @classmethod
    def _get_enclosure_device_map(cls, graph):
        """
        Get a map of enclosure devices to the devices they enclose.

        :param DiGraph graph: the graph

        :returns: a map from enclosure devices sets to their devices.
        :rtype: dict of (set of str) * (list of _Info)

        Note that _Infos are sorted by their identifier attribute.
        """
        enclosures = cls._get_enclosure_devices(graph)

        enclosure_map = dict(
           (e, list(cls._get_devices_for_enclosure(graph, e))) \
              for e in enclosures
        )

        enc_spindle_map = cls._group_enclosures(enclosure_map)
        return \
           cls._combine_enclosure_info(graph, enclosure_map, enc_spindle_map)

    @classmethod
    def _info_to_dict(cls, graph, info):
        """
        Map info to dict.

        :param DiGraph graph: the graph
        :param _Info info: info

        :returns: a dict with attributes as keys and formatted values
        :rtype: dict of str * object
        """
        return {
           'identifier' : info.identifier,
           'target' : info.target and cls._TARGET_FUNC(graph.node[info.target]),
           'disk' : info.disk,
           'devices' : [cls._DEVICES_FUNC(graph.node[d]) for d in info.devices]
        }

    @classmethod
    def get(cls, graph):
        """
        Get JSON suitable for templating.

        :param DiGraph graph: the graph
        :returns: a dict for applying to a template (JSON)
        """
        enc_dev_map = cls._get_enclosure_device_map(graph)
        keys = sorted((k for k in enc_dev_map.keys()), key=len)
        return {
           'enclosures' :
           [
              {
                 'names' :
                    sorted(
                       cls._ENCLOSURE_FUNC(graph.node[enc]) for enc in encs
                    ),
                 'disks' :
                    [cls._info_to_dict(graph, x) for x in enc_dev_map[encs]]
              } for encs in keys
           ]
        }
