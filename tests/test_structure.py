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
    tests.test_graphs
    =================

    Tests graph generation.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pydevDAG

import pytest

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

from ._constants import CONTEXT
from ._constants import EITHERS

NUM_TESTS = 5

# Use conditional to avoid processing tests if number of examples is too small.
# pytest.mark.skipif allows the test to be built, resulting in a hypothesis
# error if SLAVES or HOLDERS is empty.
@pytest.mark.skipif(
   len(EITHERS) == 0,
   reason="no slaves or holders data for tests"
)
class TestSysfsTraversal(object):
    """
    A class for testing graphs generated entirely from sysfs traversals.
    """
    @given(strategies.sampled_from(EITHERS))
    @settings(max_examples=NUM_TESTS, min_satisfying_examples=1)
    def test_slaves(self, device):
        """
        Verify slaves graph has same number of nodes as traversal.

        Traversal may contain duplicates, while graph should eliminate
        duplicates during its construction. Traversal results does not
        include origin device, graph nodes do.
        """
        slaves = list(pydevDAG.slaves(CONTEXT, device))
        graph = pydevDAG.SysfsTraversal.slaves(CONTEXT, device)
        graph_len = len(graph)
        assert len(set(slaves)) == (graph_len - 1 if graph_len else 0)

    @given(strategies.sampled_from(EITHERS))
    @settings(max_examples=NUM_TESTS, min_satisfying_examples=1)
    def test_holders(self, device):
        """
        Verify holders graph has same number of nodes as traversal.

        Traversal may contain duplicates, while graph should eliminate
        duplicates during its construction. Traversal results does not
        include origin device, graph nodes do.
        """
        holders = list(pydevDAG.holders(CONTEXT, device))
        graph = pydevDAG.SysfsTraversal.holders(CONTEXT, device)
        graph_len = len(graph)
        assert len(set(holders)) == (graph_len - 1 if graph_len else 0)

class TestSysfsGraphs(object):
    """
    Test building various graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        There is an equivalence between the nodes in the graph
        and the devices graphed.

        Moreover, all nodes have node_type DEVICE_PATH and all edges have
        type SLAVE.
        """
        graph = pydevDAG.PyudevGraphs.SYSFS_GRAPHS.complete(
           CONTEXT,
           subsystem="block"
        )

        types = nx.get_node_attributes(graph, "nodetype")
        assert all(t is pydevDAG.NodeTypes.DEVICE_PATH for t in types.values())

        types = nx.get_edge_attributes(graph, "edgetype")
        assert all(t is pydevDAG.EdgeTypes.SLAVE for t in types.values())


class TestPartitionGraphs(object):
    """
    Test the partition graph.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        The number of nodes in the graph is strictly greater than the number of
        partition devices, as partitions have to belong to some device.
        """
        graph = pydevDAG.PyudevGraphs.PARTITION_GRAPHS.complete(CONTEXT)
        block_devices = CONTEXT.list_devices(subsytem="block")
        partitions = list(block_devices.match_property('DEVTYPE', 'partition'))
        num_partitions = len(partitions)
        num_nodes = nx.number_of_nodes(graph)

        assert (num_partitions == 0 and num_nodes == 0) or \
           nx.number_of_nodes(graph) > len(partitions)


class TestSpindleGraphs(object):
    """
    Test spindle graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        Assert that the graph has no cycles.
        """
        graph = pydevDAG.PyudevGraphs.SPINDLE_GRAPHS.complete(CONTEXT)
        assert nx.is_directed_acyclic_graph(graph)


class TestDMPartitionGraphs(object):
    """
    Test device mapper partition graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        Assert that the graph has no cycles.
        """
        graph = pydevDAG.PyudevGraphs.DM_PARTITION_GRAPHS.complete(CONTEXT)
        assert nx.is_directed_acyclic_graph(graph)


class TestEnclosureGraphs(object):
    """
    Test enclosure graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_complete(self):
        """
        Assert that graph has no cycles.

        Assert that all edges have type ENCLOSUREBAY.
        """
        graph = pydevDAG.PyudevGraphs.ENCLOSURE_GRAPHS.complete(CONTEXT)
        assert nx.is_directed_acyclic_graph(graph)

        edgetypes = nx.get_edge_attributes(graph, 'edgetype')
        assert all(
           v is pydevDAG.EdgeTypes.ENCLOSUREBAY for (k, v) in edgetypes.items()
        )

        identifiers = nx.get_edge_attributes(graph, 'identifier')
        assert set(graph.edges()) == set(identifiers.keys())
