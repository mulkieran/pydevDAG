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
    pydevDAG._comparison._difference
    ================================

    Take a difference between two graphs.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

from .._attributes import DiffStatuses

from .._decorations import Decorator
from .._decorations import DifferenceMarkers


class Differences(object):
    """
    Find the differences between two graphs, if they exist.
    """

    @staticmethod
    def edge_differences(graph1, graph2, edges_equal):
        """
        Find the edge differences between graph1 and graph2 as a pair of graphs.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param edge_equal: a function that checks if two edges are equal
        :type edge_equal: `DiGraph` * `DiGraph` -> edge * edge -> bool

        :returns: a pair of graphs, representing graph1 - graph2 and vice-versa
        :rtype: tuple of `DiGraph`
        """
        diff_1 = nx.DiGraph()
        diff_2 = nx.DiGraph()

        edges_1 = graph1.edges()
        edges_2 = graph2.edges()

        edges_equal = edges_equal(graph1, graph2)

        diff_edges_1 = (n for n in edges_1 if \
           not any(edges_equal(n, o) for o in edges_2))
        diff_edges_2 = (n for n in edges_2 if \
           not any(edges_equal(n, o) for o in edges_1))

        diff_1.add_edges_from(diff_edges_1)
        diff_2.add_edges_from(diff_edges_2)

        return (diff_1, diff_2)


    @staticmethod
    def node_differences(graph1, graph2, node_equal):
        """
        Find the differences between graph1 and graph2 as a pair of graphs.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param node_equal: a function that checks if two nodes are equal
        :type node_equal: `DiGraph` * `DiGraph` -> node * node -> bool

        :returns: a pair of graphs, representing graph1 - graph2 and vice-versa
        :rtype: tuple of `DiGraph`
        """
        diff_1 = nx.DiGraph()
        diff_2 = nx.DiGraph()

        nodes_1 = graph1.nodes()
        nodes_2 = graph2.nodes()

        node_equal = node_equal(graph1, graph2)

        diff_nodes_1 = (n for n in nodes_1 if \
           not any(node_equal(n, o) for o in nodes_2))
        diff_nodes_2 = (n for n in nodes_2 if \
           not any(node_equal(o, n) for o in nodes_1))

        diff_1.add_nodes_from(diff_nodes_1)
        diff_2.add_nodes_from(diff_nodes_2)

        return (diff_1, diff_2)

    @classmethod
    def full_diff(
       cls,
       graph1,
       graph2,
       node_equal=lambda g1, g2: lambda x, y: True,
       edge_equal=lambda g1, g2: lambda x, y: True
    ):
        """
        Return a graph that shows the full difference between graph1 and graph2.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param node_equal: a function that determines if two nodes are equal
        :type node_equal: `DiGraph` * `DiGraph` -> node * node -> bool
        :param edge_equal: a function that determines if two edges are equal
        :type edge_equal: `DiGraph` * `DiGraph` -> edge * edge -> bool
        :returns: an annotated graph composed of ``graph1`` and ``graph2``
        :rtype: `DiGraph`
        """
        graph = nx.compose(graph1, graph2, name="union")

        (l_node_diff, r_node_diff) = cls.node_differences(
           graph1,
           graph2,
           node_equal
        )
        (l_edge_diff, r_edge_diff) = cls.edge_differences(
           graph1,
           graph2,
           edge_equal
        )

        removed = DifferenceMarkers.node_differences(
           graph,
           l_node_diff,
           DiffStatuses.REMOVED
        )
        Decorator.decorate_nodes(graph, removed)
        removed = DifferenceMarkers.edge_differences(
           graph,
           l_edge_diff,
           DiffStatuses.REMOVED
        )
        Decorator.decorate_edges(graph, removed)

        added = DifferenceMarkers.node_differences(
           graph,
           r_node_diff,
           DiffStatuses.ADDED
        )
        Decorator.decorate_nodes(graph, added)
        added = DifferenceMarkers.edge_differences(
           graph,
           r_edge_diff,
           DiffStatuses.ADDED
        )
        Decorator.decorate_edges(graph, added)

        return graph

    @classmethod
    def left_diff(
       cls,
       graph1,
       graph2,
       node_equal=lambda g1, g2: lambda x, y: True,
       edge_equal=lambda g1, g2: lambda x, y: True
    ):
        """
        Return a graph of the left difference between graph1 and graph2.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param node_equal: a function that determines if two nodes are equal
        :type node_equal: `DiGraph` * `DiGraph` -> node * node -> bool
        :param edge_equal: a function that determines if two edges are equal
        :type edge_equal: `DiGraph` * `DiGraph` -> edge * edge -> bool
        :returns: ``graph1`` with removed nodes marked
        :rtype: `DiGraph`
        """
        graph = graph1.copy()

        (ldiff, _) = cls.node_differences(graph1, graph2, node_equal)
        removed = DifferenceMarkers.node_differences(
           graph,
           ldiff,
           DiffStatuses.REMOVED
        )
        Decorator.decorate_nodes(graph, removed)

        (ldiff, _) = cls.edge_differences(graph1, graph2, edge_equal)
        removed = DifferenceMarkers.edge_differences(
           graph,
           ldiff,
           DiffStatuses.REMOVED
        )
        Decorator.decorate_edges(graph, removed)

        return graph

    @classmethod
    def right_diff(
       cls,
       graph1,
       graph2,
       node_equal=lambda g1, g2: lambda x, y: True,
       edge_equal=lambda g1, g2: lambda x, y: True
    ):
        """
        Return a graph of the right difference between graph1 and graph2.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param node_equal: a function that determines if two nodes are equal
        :type node_equal: `DiGraph` * `DiGraph` -> node * node -> bool
        :param edge_equal: a function that determines if two edges are equal
        :type edge_equal: `DiGraph` * `DiGraph` -> edge * edge -> bool
        :returns: ``graph2`` with added nodes marked
        :rtype: `DiGraph`
        """
        graph = graph2.copy()

        (_, rdiff) = cls.node_differences(graph1, graph2, node_equal)
        added = DifferenceMarkers.node_differences(
           graph,
           rdiff,
           DiffStatuses.ADDED
        )
        Decorator.decorate_nodes(graph, added)

        (_, rdiff) = cls.edge_differences(graph1, graph2, edge_equal)
        added = DifferenceMarkers.edge_differences(
           graph,
           rdiff,
           DiffStatuses.ADDED
        )
        Decorator.decorate_edges(graph, added)

        return graph
