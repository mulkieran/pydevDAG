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

from ._decorations import NodeDecorator

from ._config import _Config

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
        graph = _structure.PyudevAggregateGraph.graph(
           context,
           name,
           [getattr(_structure.PyudevGraphs, name) for name in graph_classes]
        )
        graph.graph['structure'] = graph_classes
        return graph

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
