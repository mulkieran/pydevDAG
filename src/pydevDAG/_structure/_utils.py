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
    pydevDAG._structure._utils
    ==========================

    Utilities for graph building.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class GraphMethods(object):
    """
    Generic graph methods.
    """

    @staticmethod
    def get_node_args(nodes, node_type):
        """
        Get node arguments, along with keys.

        :param nodes: source nodes
        :type nodes: list of object
        :param `NodeType` node_type: a node type
        :returns: arguments suitable for passing to add_nodes_from()
        """
        return (
           (n, {'nodetype' : node_type, 'identifier' : n}) \
           for n in nodes
        )

    @classmethod
    def add_nodes(cls, graph, nodes, node_type):
        """
        Add nodes in ``nodes`` to graph.

        :param `DiGraph` graph: the graph
        :param nodes: source nodes
        :type nodes: list of object
        :param `NodeType` node_type: a node type

        Nodes are device_paths of each device, as these uniquely identify
        the device.
        """
        graph.add_nodes_from(cls.get_node_args(nodes, node_type))

    @classmethod
    def add_edges( # pylint: disable=too-many-arguments
       cls,
       graph,
       sources,
       targets,
       edge_type,
       source_node_type,
       target_node_type,
       edge_attributes=None
    ):
        """
        Add edges to graph from sources to targets.

        :param `DiGraph` graph: the graph
        :param sources: source nodes
        :type sources: list of `object`
        :param targets: target nodes
        :type targets: list of `object`
        :param `EdgeType` edge_type: type for edges
        :param `NodeType` source_node_type: type for source nodes
        :param `NodeType` target_node_type: type for target nodes
        :param edge_attributes: dict of edge attributes (default None)
        :type edge_attributes: dict of str * object or NoneType
        """
        graph.add_nodes_from(cls.get_node_args(sources, source_node_type))
        graph.add_nodes_from(cls.get_node_args(targets, target_node_type))

        edges = ((x, y) for x in sources for y in targets)
        graph.add_edges_from(
           edges,
           attr_dict=edge_attributes,
           edgetype=edge_type
        )
