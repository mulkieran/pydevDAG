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

from collections import defaultdict

import networkx as nx

from ._attributes import ElementTypes
from ._attributes import NodeTypes

from ._decorations import DevlinkValues
from ._decorations import Decorator
from ._decorations import SysfsAttributes
from ._decorations import UdevProperties

from . import _compare
from . import _display
from . import _print
from . import _structure
from . import _utils


class GenerateGraph(object):
    """
    Coordinate graph generating activities.
    """

    @staticmethod
    def get_graph(context, name):
        """
        Get a complete graph storage graph.

        :param `Context` context: the libudev context
        :return: the generated graph
        :rtype: `DiGraph`
        """
        graph_classes = [
           _structure.DMPartitionGraphs,
           _structure.PartitionGraphs,
           _structure.SpindleGraphs,
           _structure.SysfsBlockGraphs
        ]
        return _structure.Graph.graph(context, name, graph_classes)

    @staticmethod
    def decorate_graph(context, graph):
        """
        Decorate a graph with additional properties.

        :param `Context` context: the libudev context
        :param `DiGraph` graph: the graph
        """
        table = dict()

        properties = ['DEVNAME', 'DEVPATH', 'DEVTYPE']
        table.update(UdevProperties.udev_properties(context, graph, properties))

        attributes = ['size', 'dm/name']
        table.update(
           SysfsAttributes.sysfs_attributes(context, graph, attributes)
        )

        categories = ['by-path']
        table.update(DevlinkValues.devlink_values(context, graph, categories))

        Decorator.decorate_nodes(graph, table)


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
        dot_graph = nx.to_agraph(graph)
        dot_graph.graph_attr.update(rankdir="LR")
        dot_graph.layout(prog="dot")

        xformers = [
           _display.SpindleTransformer,
           _display.PartitionTransformer,
           _display.PartitionEdgeTransformer,
           _display.CongruenceEdgeTransformer,
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
           _print.NodeGetters.DMNAME,
           _print.NodeGetters.DEVNAME,
           _print.NodeGetters.IDENTIFIER
        ]
        line_info = _print.GraphLineInfo(
           graph,
           ['NAME', 'DEVTYPE', 'DIFFSTATUS', 'BY-PATH', 'SIZE'],
           justification,
           {
              'NAME' : name_funcs,
              'DEVTYPE': [_print.NodeGetters.DEVTYPE],
              'DIFFSTATUS': [_print.NodeGetters.DIFFSTATUS],
              'SIZE': [_print.NodeGetters.SIZE],
              'BY-PATH': [_print.NodeGetters.BY_PATH]
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
        node_matcher = _compare.Matcher(
           ['identifier', 'nodetype'],
           ElementTypes.NODE
        )
        match_func = node_matcher.get_match
        edge_matcher = lambda g1, g2: lambda x, y: x == y
        if diff == "full":
            return _compare.Differences.full_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        elif diff == "left":
            return _compare.Differences.left_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        elif diff == "right":
            return _compare.Differences.right_diff(
               graph1,
               graph2,
               match_func,
               edge_matcher
            )
        else:
            assert False


class CompareGraph(object):
    """
    Compare graphs with boolean result.
    """

    @staticmethod
    def equivalent(graph1, graph2):
        """
        Do ``graph1`` and ``graph2`` have the same shape?

        The type of storage entity that a node represents is considered
        significant, but not its identity.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph
        :returns: True if the graphs are equivalent, otherwise False
        :rtype: bool
        """
        return _compare.Compare.is_equivalent(
           graph1,
           graph2,
           lambda x, y: x['nodetype'] is y['nodetype'],
           lambda x, y: x['edgetype'] is y['edgetype']
        )

    @staticmethod
    def identical(graph1, graph2):
        """
        Are ``graph1`` and ``graph2`` identical?

        The identity of every node matters.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph

        :returns: True if the graphs are identical, otherwise False
        :rtype: boolean
        """
        node_matcher = _compare.Matcher(
           ['identifier', 'nodetype'],
           ElementTypes.NODE
        )

        return _compare.Compare.is_equivalent(
           graph1,
           graph2,
           node_matcher.get_iso_match(),
           lambda x, y: True
        )

    @classmethod
    def compare(cls, graph1, graph2):
        """
        Calculate relationship between ``graph1`` and ``graph2``.

        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph

        :returns: 0 if identical, 1 if equivalent, otherwise 2
        :rtype: int
        """

        if cls.identical(graph1, graph2):
            return 0

        if cls.equivalent(graph1, graph2):
            return 1

        return 2


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

        def node_func(node1, node2):
            """
            :param node1: a dict of node attributes
            :type node1: dict of str * object
            :param node2: a dict of node attributes
            :type node2: dict of str * object
            :returns: True if nodes are eqivalent, otherwise False
            :rtype: bool
            """
            nodetype = node1['nodetype']

            if nodetype is not node2['nodetype']:
                return False

            if nodetype is NodeTypes.WWN:
                return node1['identifier'] == node2['identifier']
            else:
                return True

        return _compare.Compare.isomorphisms_iter(
           graph1,
           graph2,
           node_func,
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
           _print.NodeGetters.DMNAME,
           _print.NodeGetters.DEVNAME,
           _print.NodeGetters.IDENTIFIER
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
