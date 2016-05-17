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

import os

from collections import defaultdict

import networkx

from ._decorations import NodeDecorator

from ._config import _Config

from . import _display
from . import _item_str
from . import _print
from . import _structure


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
