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
    pydevDAG._structure._pyudev._utils
    ==================================

    Utilities for building pyudev graphs.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

import networkx as nx

from .._utils import GraphMethods

from ... import _traversal

from ..._attributes import EdgeTypes
from ..._attributes import NodeTypes


SysfsTraversalConfig = namedtuple(
   'SysfsTraversalConfig',
   ['recursive', 'slaves']
)


class SysfsTraversal(object):
    """
    Build simple graph from the holders or slaves of a given device.
    """

    @classmethod
    def do_level(cls, graph, context, device, config):
        """
        Recursively defined function to generate a graph from ``device``.

        :param `DiGraph` graph: the graph
        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param `SysfsTraversalConfig` config: traversal configuration
        """
        func = _traversal.slaves if config.slaves else _traversal.holders
        level = list(func(context, device, False))

        if config.slaves:
            sources = [device]
            targets = level
        else:
            sources = level
            targets = [device]

        if not level:
            GraphMethods.add_nodes(
               graph,
               [device.device_path],
               NodeTypes.DEVICE_PATH
            )
            return

        GraphMethods.add_edges(
           graph,
           [dev.device_path for dev in sources],
           [dev.device_path for dev in targets],
           EdgeTypes.SLAVE,
           NodeTypes.DEVICE_PATH,
           NodeTypes.DEVICE_PATH
        )

        if config.recursive:
            for dev in level:
                cls.do_level(graph, context, dev, config)

    @classmethod
    def sysfs_traversal(cls, context, device, config):
        """
        General graph of a sysfs traversal.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param `SysfsTraversalConfig` config: traversal configuration
        :returns: a graph
        :rtype: `DiGraph`
        """
        graph = nx.DiGraph()
        cls.do_level(graph, context, device, config)
        return graph

    @classmethod
    def holders(cls, context, device, recursive=True):
        """
        Yield graph of slaves of device, including the device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `DiGraph`
        """
        config = SysfsTraversalConfig(slaves=False, recursive=recursive)
        return cls.sysfs_traversal(context, device, config)

    @classmethod
    def slaves(cls, context, device, recursive=True):
        """
        Yield graph of slaves of device, including the device.

        :param `Context` context: the libudev context
        :param `Device` device: the device
        :param bool recursive: True for recursive, False otherwise
        :returns: a graph
        :rtype: `DiGraph`
        """
        config = SysfsTraversalConfig(slaves=True, recursive=recursive)
        return cls.sysfs_traversal(context, device, config)
