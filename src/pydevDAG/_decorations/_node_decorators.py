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

import sys

from itertools import groupby

import six

import networkx as nx

import pyudev

from pydevDAG._attributes import NodeTypes

from ._devlink import Devlink

class UdevProperties(object):
    """
    Find udev properties for the device nodes of a network graph.
    """

    @staticmethod
    def decorated(graph):
        """
        Returns elements that get decorated.
        """
        node_types = nx.get_node_attributes(graph, 'nodetype')
        return (k for k in node_types \
           if node_types[k] is NodeTypes.DEVICE_PATH)

    @staticmethod
    def properties(context, element, names):
        """
        Get properties on this element.

        :returns: a map of udev properties
        :rtype: dict
        """
        try:
            device = pyudev.Device.from_path(context, element)
        except pyudev.DeviceNotFoundError:
            return dict()

        return dict((k, device[k]) for k in names if k in device)

    @classmethod
    def udev_properties(cls, context, graph, names):
        """
        Get udev properties for graph nodes that correspond to devices.

        :param `Context` context: the udev context
        :param graph: the graph
        :param names: a list of property keys
        :type names: list of str

        :returns: dict of property name, node, property value
        :rtype: dict
        """
        udev_dict = dict()
        for node in cls.decorated(graph):
            udev_dict[node] = cls.properties(context, node, names)

        return {'UDEV' : udev_dict}


class SysfsAttributes(object):
    """
    Find sysfs attributes for the device nodes of a network graph.
    """

    @staticmethod
    def decorated(graph):
        """
        Returns elements that get decorated.
        """
        node_types = nx.get_node_attributes(graph, 'nodetype')
        return (k for k in node_types \
           if node_types[k] is NodeTypes.DEVICE_PATH)

    @staticmethod
    def attributes(context, element, names):
        """
        Get attributes on this element.

        :returns: a map of sysfs attributes
        :rtype: dict of str * (str or NoneType)
        """
        try:
            device = pyudev.Device.from_path(context, element)
        except pyudev.DeviceNotFoundError:
            return dict()

        attributes = device.attributes

        res = dict()
        for key in names:
            try:
                val = attributes.get(key)
                if val is not None and not isinstance(val, six.text_type):
                    val = val.decode(sys.getfilesystemencoding())
                res[key] = val
            except UnicodeDecodeError:
                pass
        return res

    @classmethod
    def sysfs_attributes(cls, context, graph, names):
        """
        Get sysfs attributes for graph nodes that correspond to devices.

        :param `Context` context: the udev context
        :param graph: the graph
        :param names: a list of property keys
        :type names: list of str

        :returns: dict of property name, node, property value
        :rtype: dict
        """
        attribute_dict = dict()
        for node in cls.decorated(graph):
            attribute_dict[node] = cls.attributes(context, node, names)

        return {'SYSFS' : attribute_dict}


class DevlinkValues(object):
    """
    Add the informational part of device links to the graph.
    """

    @staticmethod
    def decorated(graph):
        """
        Returns elements that get decorated.
        """
        node_types = nx.get_node_attributes(graph, 'nodetype')
        return (k for k in node_types \
           if node_types[k] is NodeTypes.DEVICE_PATH)

    @staticmethod
    def values(context, element, categories):
        """
        Get device links values on this element.

        :returns: a map of devicelinks values
        :rtype: dict of str * (list of str * NoneType)
        """
        try:
            device = pyudev.Device.from_path(context, element)
        except pyudev.DeviceNotFoundError:
            return dict()

        def key_func(link):
            """
            :returns: category of link, or "" if no category
            :rtype: str
            """
            key = link.category
            return key if key is not None else ""

        devlinks = sorted(
           (Devlink(d) for d in device.device_links),
           key=key_func
        )
        link_hash = dict((k, list(g)) for (k, g) in groupby(devlinks, key_func))
        return dict((c, link_hash.get(c)) for c in categories)

    @classmethod
    def devlink_values(cls, context, graph, categories):
        """
        Get devlink values for graph nodes that correspond to devices.

        :param `Context` context: the udev context
        :param graph: the graph
        :param categories: a list of devlink categories
        :type categories: list of str

        :returns: dict of property name, node, property value
        :rtype: dict of str * str * ((list of str) or NoneType)
        """
        devlink_dict = dict()
        for node in cls.decorated(graph):
            devlink_dict[node] = cls.values(context, node, categories)

        return {'DEVLINK' : devlink_dict}
