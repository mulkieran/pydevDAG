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
    pydevDAG._decorations._node_decorators
    ======================================

    Tools to decorate networkx graphs in situ, i.e., as
    constructed rather than as read from a textual file.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

from itertools import groupby

import six

import pyudev

from pydevDAG._attributes import NodeTypes

from pydevDAG._errors import DAGValueError


@six.add_metaclass(abc.ABCMeta)
class Domain(object):
    """
    A particular domain for decoration.

    A domain is just a particular way of going about gathering the information
    to use to decorate.

    All decoration objects in a particular domain require the same setup and
    will share the same interface.
    """

    @classmethod
    def name(cls):
        """
        The name of the domain.
        """
        return cls.__name__

    @abc.abstractmethod
    def decorate(self, node, attrdict): # pragma: no cover
        """
        Updates attributes on a node.

        :param str node: the node
        :param dict attrdict: dict of node attributes
        """
        raise NotImplementedError()


class Pyudev(Domain):
    """
    Construct functions for decorating using pyudev.
    """
    # pylint: disable=too-few-public-methods


    def __init__(self, info_map):
        """
        Initializer.

        :param objects: a list of object that require a pyudev device
        """
        self.info_map = info_map
        self.context = pyudev.Context()

    def decorate(self, node, attrdict):
        try:
            device = pyudev.Device.from_path(self.context, node)
        except pyudev.DeviceNotFoundError: # pragma: no cover
            return

        for (name, (types, func)) in self.info_map.items():
            if attrdict['nodetype'] in types:
                try:
                    attrdict[name] = func(device)
                except (KeyError, UnicodeDecodeError, ValueError): # pragma: no cover
                    attrdict[name] = None


class NodeDecorator(object):
    """
    A node decorator for a particular configuration.
    """

    _FUNCTIONS = {
       'DEVNAME':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('DEVNAME'))),
       'DEVNO':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.device_number)),
       'DEVPATH':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('DEVPATH'))),
       'DEVTYPE':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('DEVTYPE'))),
       'DM_NAME':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('DM_NAME'))),
       'DM_UUID':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('DM_UUID'))),
       'DRIVER':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.driver)),
       'ID_PATH':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('ID_PATH'))),
       'ID_SAS_PATH':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.get('ID_SAS_PATH'))),
       'SUBSYSTEM':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.subsystem)),
       'SYSNAME':
          (Pyudev, ((NodeTypes.DEVICE_PATH,), lambda x: x.sys_name)),
       'size':
          (
             Pyudev,
             ((NodeTypes.DEVICE_PATH,), lambda x: x.attributes.asint('size'))
          )
    }

    def __init__(self, config):
        """
        Initializer.

        :param config: configuration for node decorators
        :type config: dict (JSON)
        """
        # list of tuple of NodeType * dict
        nodeconfigs = \
           [(NodeTypes.get_value(k["nodetype"]), k['fields']) for k in config]
        configs = [(k, v) for (k, v) in nodeconfigs if k is not None]

        # map of NodeType * (list of Domain)
        self.table = dict((k, self.get_decorator(v)) for (k, v) in configs)

    def get_decorator(self, fields):
        """
        Get a decorator for one particular nodetype.

        :param fields: fields for decorating this device type
        :type fields: list of str

        :returns: a sequence of objects for decorating
        :rtype: list of Domain
        """
        # get the functions that obtain the values
        try:
            field_map = ((field, self._FUNCTIONS[field]) for field in fields)
        except KeyError as err: # pragma: no cover
            raise DAGValueError(err)

        # sort the functions by domain
        domain_pairs = \
           groupby(sorted(field_map, key=lambda x: x[1][0]), lambda x: x[1][0])

        # construct a domain object from its component objects
        return [
           domain(dict((name, other) for (name, (domain, other)) in l)) for \
              (domain, l) in domain_pairs
        ]

    def decorate(self, node, attrdict):
        """
        Decorates ``attrdict`` with additional attributes.

        :param Context context: a pyudev context
        :param str node: the node
        :param dict attrdict: dict of node attributes
        """
        objects = self.table.get(attrdict['nodetype'])
        if objects is not None:
            for obj in  objects:
                obj.decorate(node, attrdict)
