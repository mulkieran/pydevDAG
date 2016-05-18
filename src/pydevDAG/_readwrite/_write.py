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
    pydevDAG._readwrite._write
    ==========================

    Tools to modify a graph for caching.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

from six import add_metaclass

import networkx as nx

from parseudev import Devlink

from pydevDAG._attributes import EdgeTypes
from pydevDAG._attributes import NodeTypes


@add_metaclass(abc.ABCMeta)
class ElementRewriter(object):
    """
    Generic interface of an element rewriter.
    """

    @staticmethod
    @abc.abstractmethod
    def stringize(graph, ele):
        """
        Convert attributes of this element to strings.

        :param ele: a graph element
        """
        raise NotImplementedError() # pragma: no cover

    @staticmethod
    @abc.abstractmethod
    def destringize(graph, ele):
        """
        Inverse of stringize.

        :param ele: a graph element
        """
        raise NotImplementedError() # pragma: no cover


class DefaultRewriters(object):
    """
    Generates the most likely rewriter for nodes.
    """

    @staticmethod
    def rewrite_node_gen(graph, node, key, func):
        """
        Default way of rewriting a node.

        Assumes that the key and value are at the top level.

        :param graph: the graph
        :param node: a single node
        :param str key: the key of the graph attribute
        :param func: the func that gives new value for attribute value
        :type func: object -> object
        """
        try:
            value = graph.node[node][key]
        except KeyError: # pragma: no cover
            return
        graph.node[node][key] = func(value)

    @staticmethod
    def rewrite_edge_gen(graph, edge, key, func):
        """
        Default way of rewriting an edge.

        Assumes that the key and value are at the top level.

        :param graph: the graph
        :param edge: a single edge
        :param str key: the key of the graph attribute
        :param func: the func that gives new value for attribute value
        :type func: object -> object
        """
        source = edge[0]
        target = edge[1]
        try:
            value = graph[source][target][key]
        except KeyError: # pragma: no cover
            return
        graph[source][target][key] = func(value)


class NodeTypeRewriter(ElementRewriter):
    """
    Rewrites node type.
    """

    @staticmethod
    def stringize(graph, node):
        return DefaultRewriters.rewrite_node_gen(graph, node, 'nodetype', str)

    @staticmethod
    def destringize(graph, node):
        return DefaultRewriters.rewrite_node_gen(
           graph,
           node,
           'nodetype',
           NodeTypes.get_value
        )

class DevlinkRewriter(ElementRewriter):
    """
    Rewrites device links attributes.
    """

    @staticmethod
    def stringize(graph, node):
        try:
            devlink = graph.node[node]['DEVLINK']
        except KeyError:
            return
        for key, value in devlink.items():
            devlink[key] = None if value is None else [str(d) for d in value]

    @staticmethod
    def destringize(graph, node):
        try:
            devlink = graph.node[node]['DEVLINK']
        except KeyError:
            return
        for key, value in devlink.items():
            devlink[key] = \
               None if value is None else [Devlink(d) for d in value]

class EdgeTypeRewriter(ElementRewriter):
    """
    Rewrites edge type.
    """

    @staticmethod
    def stringize(graph, edge):
        return DefaultRewriters.rewrite_edge_gen(graph, edge, 'edgetype', str)

    @staticmethod
    def destringize(graph, edge):
        return DefaultRewriters.rewrite_edge_gen(
           graph,
           edge,
           'edgetype',
           EdgeTypes.get_value
        )

class Rewriter(object):
    """
    Rewrite graph for output.
    """
    # pylint: disable=too-few-public-methods

    _NODE_REWRITERS = [
       DevlinkRewriter,
       NodeTypeRewriter
    ]

    _EDGE_REWRITERS = [
       EdgeTypeRewriter
    ]

    @classmethod
    def _rewrite(cls, graph, stringize):
        """
        Rewrite objects in graph.

        :param graph: the graph
        :param bool stringize: if True, stringize, otherwise destringize
        """
        if stringize:
            node_methods = [r.stringize for r in cls._NODE_REWRITERS]
            edge_methods = [r.stringize for r in cls._EDGE_REWRITERS]
        else:
            node_methods = [r.destringize for r in cls._NODE_REWRITERS]
            edge_methods = [r.destringize for r in cls._EDGE_REWRITERS]

        for node in nx.nodes_iter(graph):
            for rewriter in node_methods:
                rewriter(graph, node)

        for edge in nx.edges_iter(graph):
            for rewriter in edge_methods:
                rewriter(graph, edge)

    @classmethod
    def stringize(cls, graph):
        """
        Xform objects in graph to strings as necessary.
        :param graph: the graph
        """
        cls._rewrite(graph, True)

    @classmethod
    def destringize(cls, graph):
        """
        Xform objects in graph to strings as necessary.
        :param graph: the graph
        """
        cls._rewrite(graph, False)
