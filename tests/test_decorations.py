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
    tests.test_decorations
    ======================

    Tests graph decorations.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import networkx

import pydevDAG

from ._constants import GRAPH


class TestGraphNodeDecorations(object):
    """
    Test decorating structure graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_devpath(self):
        """
        Test that the value of DEVPATH is the same as the key of the node.
        """
        graph = GRAPH.copy()
        decorator = pydevDAG.NodeDecorator(
            json.loads('{"DevicePath" : {"UDEV": {"args": ["DEVPATH"]}}}')
        )
        for node in graph.nodes():
            decorator.decorate(node, graph.node[node])
        for node in graph.nodes():
            nodetype = graph.node[node]['nodetype']
            assert nodetype is not pydevDAG.NodeTypes.DEVICE_PATH or \
               pydevDAG.Dict.get_value(graph.node[node], ["UDEV", "DEVPATH"]) \
               == node


class TestNodeDecorating(object):
    """
    Test actually decorating a graph.
    """

    def test_decorating_nodes(self):
        """
        Test that decorating actually sets the proper value.
        """
        new_graph = GRAPH.copy()
        properties = {
           "dummy": dict((n, "dummy") for n in new_graph)
        }
        pydevDAG.Decorator.decorate_nodes(new_graph, properties)
        values = networkx.get_node_attributes(new_graph, "dummy").values()
        assert values and all(n == "dummy" for n in values)

        others = networkx.get_node_attributes(GRAPH, "dummy").values()
        assert not others

    def test_decorating_edges(self):
        """
        Test that decorating actually sets the proper value.
        """
        new_graph = GRAPH.copy()
        properties = {
           "dummy": dict((e, "dummy") for e in new_graph.edges())
        }
        pydevDAG.Decorator.decorate_edges(new_graph, properties)
        values = networkx.get_edge_attributes(new_graph, "dummy").values()
        assert values and all(e == "dummy" for e in values)

        others = networkx.get_edge_attributes(GRAPH, "dummy").values()
        assert not others
