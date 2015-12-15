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
    tests.test_compare
    ==================

    Tests graph comparison.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import pydevDAG

from ._constants import GRAPH


class TestGraphComparison(object):
    """
    Compare storage graphs more or less stringently.
    """
    # pylint: disable=too-few-public-methods

    def test_equal(self, tmpdir):
        """
        Verify that two identical graphs are equivalent.
        """
        node_matcher = pydevDAG.Matcher(['identifier', 'nodetype'], 'node')
        edge_matcher = pydevDAG.Matcher(['edgetype'], 'edge')

        new_graph = GRAPH.copy()
        filepath = str(tmpdir.join('test.gml'))
        with open(filepath, 'w') as out:
            pydevDAG.Writer.write(new_graph, out)

        with open(filepath, 'r') as infile:
            graph1 = pydevDAG.Reader.read(infile)
        with open(filepath, 'r') as infile:
            graph2 = pydevDAG.Reader.read(infile)

        assert pydevDAG.Compare.is_equivalent(
           graph1,
           graph2,
           node_matcher.get_iso_match(),
           edge_matcher.get_iso_match()
        )


class TestGraphDifference(object):
    """
    Test ability to find differences among graphs.
    """

    NODE_MATCHER = pydevDAG.Matcher(['identifier', 'nodetype'], 'node')
    EDGE_MATCHER = pydevDAG.Matcher(['edgetype'], 'edge')

    def test_equal(self, tmpdir):
        """
        Verify that two identical graphs are equivalent.
        """
        new_graph = GRAPH.copy()
        filepath = str(tmpdir.join('test.gml'))
        with open(filepath, 'w') as out:
            pydevDAG.Writer.write(new_graph, out)

        with open(filepath, 'r') as infile:
            graph1 = pydevDAG.Reader.read(infile)
        with open(filepath, 'r') as infile:
            graph2 = pydevDAG.Reader.read(infile)

        (diff1, diff2) = pydevDAG.Differences.node_differences(
           graph1,
           graph2,
           self.NODE_MATCHER.get_match
        )
        assert len(diff1) == 0 and len(diff2) == 0
        (diff1, diff2) = pydevDAG.Differences.edge_differences(
           graph1,
           graph2,
           self.EDGE_MATCHER.get_match
        )
        assert len(diff1) == 0 and len(diff2) == 0

        full_diff = pydevDAG.Differences.full_diff(
           graph1,
           graph2,
           self.NODE_MATCHER.get_match
        )
        assert pydevDAG.Compare.is_equivalent(
           full_diff,
           graph1,
           self.NODE_MATCHER.get_iso_match(),
           self.EDGE_MATCHER.get_iso_match()
        )
        statuses = nx.get_node_attributes(full_diff, "diffstatus")
        assert not any(statuses[k] is pydevDAG.DiffStatuses.REMOVED \
           for k in statuses)
        assert not any(statuses[k] is pydevDAG.DiffStatuses.ADDED \
           for k in statuses)

        left_diff = pydevDAG.Differences.left_diff(
           graph1,
           graph2,
           self.NODE_MATCHER.get_match
        )
        assert pydevDAG.Compare.is_equivalent(
           left_diff,
           graph1,
           self.NODE_MATCHER.get_iso_match(),
           self.EDGE_MATCHER.get_iso_match()
        )
        statuses = nx.get_node_attributes(left_diff, "diffstatus")
        assert not any(statuses[k] is pydevDAG.DiffStatuses.REMOVED \
           for k in statuses)
        assert not any(statuses[k] is pydevDAG.DiffStatuses.ADDED \
           for k in statuses)

        right_diff = pydevDAG.Differences.right_diff(
           graph1,
           graph2,
           self.NODE_MATCHER.get_match
        )
        assert pydevDAG.Compare.is_equivalent(
           right_diff,
           graph1,
           self.NODE_MATCHER.get_iso_match(),
           self.EDGE_MATCHER.get_iso_match()
        )
        statuses = nx.get_node_attributes(right_diff, "diffstatus")
        assert not any(statuses[k] is pydevDAG.DiffStatuses.REMOVED \
           for k in statuses)
        assert not any(statuses[k] is pydevDAG.DiffStatuses.ADDED \
           for k in statuses)

    def test_empty(self):
        """
        Verify that one graph and an empty graph have the correct differences.
        """
        empty_graph = nx.DiGraph()

        (diff1, diff2) = pydevDAG.Differences.node_differences(
           GRAPH,
           empty_graph,
           self.NODE_MATCHER.get_match
        )

        assert sorted(diff1.nodes()) == sorted(GRAPH.nodes())
        assert sorted(diff2.nodes()) == sorted(empty_graph.nodes())

        (diff1, diff2) = pydevDAG.Differences.edge_differences(
           GRAPH,
           empty_graph,
           self.NODE_MATCHER.get_match
        )
        assert sorted(diff1.edges()) == sorted(GRAPH.edges())
        assert sorted(diff2.edges()) == sorted(empty_graph.edges())

        full_diff = pydevDAG.Differences.full_diff(
           GRAPH,
           empty_graph,
           self.NODE_MATCHER.get_match
        )
        statuses = nx.get_node_attributes(full_diff, "diffstatus")
        assert all(
           statuses[k] is pydevDAG.DiffStatuses.REMOVED for k in statuses
        )
        assert len(statuses) == len(GRAPH)

        full_diff = pydevDAG.Differences.full_diff(
           empty_graph,
           GRAPH,
           self.NODE_MATCHER.get_match
        )
        statuses = nx.get_node_attributes(full_diff, "diffstatus")
        assert all(statuses[k] is pydevDAG.DiffStatuses.ADDED for k in statuses)
        assert len(statuses) == len(GRAPH)

        left_diff = pydevDAG.Differences.left_diff(
           GRAPH,
           empty_graph,
           self.NODE_MATCHER.get_match
        )
        statuses = nx.get_node_attributes(left_diff, "diffstatus")
        assert all(
           statuses[k] is pydevDAG.DiffStatuses.REMOVED for k in statuses
        )
        assert len(statuses) == len(GRAPH)

        left_diff = pydevDAG.Differences.left_diff(
           empty_graph,
           GRAPH,
           self.NODE_MATCHER.get_match
        )
        assert left_diff.order() == 0

        right_diff = pydevDAG.Differences.right_diff(
           empty_graph,
           GRAPH,
           self.NODE_MATCHER.get_match
        )
        statuses = nx.get_node_attributes(right_diff, "diffstatus")
        assert all(statuses[k] is pydevDAG.DiffStatuses.ADDED for k in statuses)
        assert len(statuses) == len(GRAPH)

        right_diff = pydevDAG.Differences.right_diff(
           GRAPH,
           empty_graph,
           self.NODE_MATCHER.get_match
        )
        assert right_diff.order() == 0
