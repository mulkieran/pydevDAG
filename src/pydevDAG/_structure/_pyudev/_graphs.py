# -*- coding: utf-8 -*-
# Copyright (C) 2015  Red Hat, Inc.
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
    pydevDAG._structure._pyudev._graphs
    ===================================

    Individual graph classes.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from itertools import chain

import networkx as nx

from ._types import PyudevGraph
from ._utils import SysfsTraversal

from .._utils import GraphMethods

from ..._attributes import EdgeTypes
from ..._attributes import NodeTypes


class SysfsGraphs(PyudevGraph):
    """
    Build sysfs graphs in various ways.
    """

    @staticmethod
    def slaves_and_holders(context, device, recursive=True):
        """
        Make a graph of slaves and holders of a device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `DiGraph`
        """
        return nx.compose(
           SysfsTraversal.slaves(context, device, recursive),
           SysfsTraversal.holders(context, device, recursive)
        )

    @classmethod
    def parents_and_children(cls, context, device):
        """
        Make a graph of the parents and children of a device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :returns: a graph
        :rtype: `DiGraph`
        """
        return cls.slaves_and_holders(context, device, recursive=False)

    @classmethod
    def complete(cls, context, **kwargs):
        devices = (d for d in context.list_devices(**kwargs))
        graphs = (cls.parents_and_children(context, d) for d in devices)
        return nx.compose_all(chain([nx.DiGraph()], graphs), name="sysfs")


class SysfsBlockGraphs(PyudevGraph): # pragma: no cover
    """
    Composes holders/slaves graphs for block devices.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def complete(cls, context, **kwargs):
        return SysfsGraphs.complete(context, subsystem="block")


class PartitionGraphs(PyudevGraph):
    """
    Build graphs of partition relationships.
    """

    @staticmethod
    def partition_graph(device):
        """
        Make a graph of partition relationships.

        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()
        parent = device.parent
        GraphMethods.add_edges(
           graph,
           [device.device_path],
           [parent.device_path],
           EdgeTypes.PARTITION,
           NodeTypes.DEVICE_PATH,
           NodeTypes.DEVICE_PATH
        )
        return graph

    @classmethod
    def complete(cls, context, **kwargs):
        block_devices = context.list_devices(subsystem="block")
        partitions = block_devices.match_property('DEVTYPE', 'partition')
        graphs = (cls.partition_graph(d) for d in partitions)
        return nx.compose_all(chain([nx.DiGraph()], graphs), name="partiton")


class SpindleGraphs(PyudevGraph):
    """
    Build graphs of relationships with actual physical disks.
    """

    @staticmethod
    def spindle_graph(device):
        """
        Make a graph of spindle relationships.

        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()

        wwn = device.get('ID_WWN_WITH_EXTENSION')
        if wwn is None:
            return graph

        GraphMethods.add_edges(
           graph,
           [device.device_path],
           [wwn],
           EdgeTypes.SPINDLE,
           NodeTypes.DEVICE_PATH,
           NodeTypes.WWN
        )
        return graph

    @classmethod
    def complete(cls, context, **kwargs):
        block_devices = context.list_devices(subsystem="block")
        disks = block_devices.match_property('DEVTYPE', 'disk')
        graphs = (cls.spindle_graph(d) for d in disks)
        return nx.compose_all(chain([nx.DiGraph()], graphs), name='spindle')


class DMPartitionGraphs(PyudevGraph):
    """
    Build graphs of relationships between device mapper devices and partitions.
    """

    @staticmethod
    def congruence_graph(context, device):
        """
        Build a graph of congruence relation between device mapper devices and
        partition devices.

        :param `Context` context: a udev context
        :param `Device` device: the partition device
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()

        id_part_entry_uuid = device.get('ID_PART_ENTRY_UUID')
        if id_part_entry_uuid is None:
            return graph

        block_devices = context.list_devices(subsystem="block")
        disks = block_devices.match_property('DEVTYPE', 'disk')

        block_devices = context.list_devices(subsystem="block")
        matches = block_devices.match_property(
           'ID_PART_ENTRY_UUID',
           id_part_entry_uuid
        )

        sources = set(disks) & set(matches)

        GraphMethods.add_edges(
           graph,
           [dev.device_path for dev in sources],
           [device.device_path],
           EdgeTypes.CONGRUENCE,
           NodeTypes.DEVICE_PATH,
           NodeTypes.DEVICE_PATH
        )

        return graph

    @classmethod
    def complete(cls, context, **kwargs):
        block_devices = context.list_devices(subsystem="block")
        partitions = block_devices.match_property('DEVTYPE', 'partition')
        graphs = (cls.congruence_graph(context, d) for d in partitions)
        return nx.compose_all(chain([nx.DiGraph()], graphs), name='congruence')


class PyudevGraphs(object):
    """
    Classes that build pyudev based graphs.
    """
    # pylint: disable=too-few-public-methods

    DM_PARTITION_GRAPHS = DMPartitionGraphs
    PARTITION_GRAPHS = PartitionGraphs
    SPINDLE_GRAPHS = SpindleGraphs
    SYSFS_BLOCK_GRAPHS = SysfsBlockGraphs
    SYSFS_GRAPHS = SysfsGraphs

    @classmethod
    def CLASSES(cls): # pylint: disable=invalid-name
        """
        All classes that implement PyudevGraph.
        """
        return [
           cls.DM_PARTITION_GRAPHS,
           cls.PARTITION_GRAPHS,
           cls.SPINDLE_GRAPHS,
           cls.SYSFS_BLOCK_GRAPHS,
           cls.SYSFS_GRAPHS
        ]
