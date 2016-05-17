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
    pydevDAG._graphs
    ================

    Tools to build graphs of various kinds.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import os

from collections import defaultdict

import networkx

from ._attributes import ElementTypes

from ._decorations import NodeDecorator

from ._config import _Config

from . import _comparison
from . import _display
from . import _item_str
from . import _print
from . import _structure
from . import _utils


class GenerateGraph(object):
    """
    Coordinate graph generating activities.
    """

    CONFIG = _Config(
        os.path.join(os.path.dirname(__file__), 'data/config.json')
    )

    @classmethod
    def get_graph(cls, context, name):
        """
        Get a complete graph storage graph.

        :param `Context` context: the libudev context
        :return: the generated graph
        :rtype: `DiGraph`
        """
        graph_classes = cls.CONFIG.get_graph_type_spec()
        return _structure.PyudevAggregateGraph.graph(
           context,
           name,
           [getattr(_structure.PyudevGraphs, name) for name in graph_classes]
        )

    @classmethod
    def decorate_graph(cls, graph):
        """
        Decorate a graph with additional properties.

        :param `DiGraph` graph: the graph
        """
        spec = cls.CONFIG.get_node_decoration_spec()
        decorator = NodeDecorator(spec)

        for node in graph.nodes():
            decorator.decorate(node, graph.node[node])

        graph.graph['decorations'] = spec


class CompareGraph(_comparison.CompareGraph):
    """
    Graph comparison.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initializer.
        """
        config = _Config(
            os.path.join(os.path.dirname(__file__), 'data/config.json')
        )
        spec = config.get_persistant_attributes_spec()
        super(CompareGraph, self).__init__(spec)


class DisplayGraph(object):
    """
    Displaying a generated multigraph by transformation to a graphviz graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def convert_graph(graph):
        """
        Convert graph to graphviz format.

        :param `DiGraph` graph: the graph
        :returns: a graphviz graph

        Designate its general layout and mark or rearrange nodes as appropriate.
        """
        dot_graph = networkx.to_agraph(graph) # pylint: disable=no-member
        dot_graph.graph_attr.update(rankdir="LR")
        dot_graph.layout(prog="dot")

        xformers = [
           _display.SpindleTransformer,
           _display.PartitionTransformer,
           _display.PartitionEdgeTransformer,
           _display.CongruenceEdgeTransformer,
           _display.EnclosureBayTransformer,
           _display.EnclosureTransformer,
           _display.AddedNodeTransformer,
           _display.RemovedNodeTransformer,
           _display.AddedEdgeTransformer,
           _display.RemovedEdgeTransformer
        ]

        _display.GraphTransformers.xform(dot_graph, xformers)
        return dot_graph


class PrintGraph(object):
    """
    Print a textual representation of the graph.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def print_graph(out, graph):
        """
        Print a graph.

        :param `file` out: print destination
        :param `DiGraph` graph: the graph
        """
        justification = defaultdict(lambda: '<')
        justification['SIZE'] = '>'
        name_funcs = [
           _item_str.NodeGetters.DMNAME,
           _item_str.NodeGetters.DEVNAME,
           _item_str.NodeGetters.SYSNAME,
           _item_str.NodeGetters.IDENTIFIER
        ]
        path_funcs = [
           _item_str.NodeGetters.IDSASPATH,
           _item_str.NodeGetters.IDPATH
        ]
        line_info = _print.GraphLineInfo(
           graph,
           [
              'NAME',
              'DEVNAME',
              'SUBSYSTEM',
              'DEVTYPE',
              'DIFFSTATUS',
              'DM_SUBSYSTEM',
              'ID_PATH',
              'SIZE'
           ],
           justification,
           {
              'NAME' : name_funcs,
              'DEVNAME' : [_item_str.NodeGetters.DEVNAME],
              'DEVTYPE': [_item_str.NodeGetters.DEVTYPE],
              'DM_SUBSYSTEM' : [_item_str.NodeGetters.DMUUIDSUBSYSTEM],
              'DIFFSTATUS': [_item_str.NodeGetters.DIFFSTATUS],
              'ID_PATH' : path_funcs,
              'SIZE': [_item_str.NodeGetters.SIZE],
              'SUBSYSTEM': [_item_str.NodeGetters.SUBSYSTEM]
           }
        )

        lines = _print.GraphLineArrangements.node_strings_from_graph(
           _print.GraphLineArrangementsConfig(
              line_info.info,
              lambda k, v: str(v),
              'NAME'
           ),
           graph
        )

        lines = list(_print.GraphXformLines.xform(line_info.keys, lines))
        lines = _print.Print.lines( # pylint: disable=redefined-variable-type
           line_info.keys,
           lines,
           2,
           line_info.alignment
        )
        for line in lines:
            print(line, end="\n", file=out)


class DiffGraph(object):
    """
    Take the difference of two graphs.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def do_diff(graph1, graph2, diff):
        """
        Generate the appropriate graph.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :param str diff: the diff to perform
        """
        node_matcher = _comparison.Matcher(
           ['identifier', 'nodetype'],
           ElementTypes.NODE
        )
        match_func = node_matcher.get_match
        edge_matcher = lambda g1, g2: lambda x, y: x == y
        if diff == "full":
            return _comparison.Differences.full_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        elif diff == "left":
            return _comparison.Differences.left_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        elif diff == "right":
            return _comparison.Differences.right_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        else:
            assert False


class GraphIsomorphism(object):
    """
    Get isomorphisms between two graphs.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def isomorphisms_iter(graph1, graph2):
        """
        Isomorphisms between ``graph1`` and ``graph2``.

        The type of storage entity that a node represents is considered
        significant, but not its identity, unless it is a disk with a WWN.

        It should always be the case that WWN nodes map to each other.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :returns: generator of graph isomorphisms
        :rtype: generator of dict of node * node
        """

        return _comparison.Isomorphisms.isomorphisms_iter(
           graph1,
           graph2,
           _comparison.NodeComparison([]).equivalent,
           lambda x, y: x['edgetype'] is y['edgetype']
        )

    @staticmethod
    def _minimized_isos(isos, maxnum):
        """
        Returns a generator of minimized isos, no longer than ``maxnum``.

        :param isos: an iterable of isos
        :param int maxnum: the maximum number to yield
        """
        return itertools.islice(
           (_utils.GeneralUtils.minimize_mapping(iso) for iso in isos),
           0,
           maxnum
        )

    @classmethod
    def print_isomorphism(cls, out, graph1, graph2):
        """
        Print the first isomorphism, if any.

        :param `file` out: print destination
        :param DiGraph graph1: the first graph
        :param DiGraph graph2: the second graph
        """
        isos = cls.isomorphisms_iter(graph1, graph2)
        minimized = list(cls._minimized_isos(isos, 10))

        if len(minimized) is 0:
            print('No isomorphism discovered.', end="\n", file=out)
            return

        isomorphism = min(minimized, key=len)

        name_funcs = [
           _item_str.NodeGetters.DMNAME,
           _item_str.NodeGetters.DEVNAME,
           _item_str.NodeGetters.IDENTIFIER
        ]
        mapinfo = _print.MapLineInfos(
           graph1,
           graph2,
           name_funcs,
           ('GRAPH 1', 'GRAPH 2')
        )
        lines = mapinfo.info(isomorphism)
        lines = _print.Print.lines( # pylint: disable=redefined-variable-type
           mapinfo.keys,
           lines,
           2,
           {'GRAPH 1' : '<', 'GRAPH 2' : '>'}
        )
        for line in lines:
            print(line, end="\n", file=out)
