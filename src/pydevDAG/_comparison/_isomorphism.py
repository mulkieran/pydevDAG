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
    pydevDAG._comparison._isomorphism
    =================================

    Discover isomorphisms between graphs.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx.algorithms.isomorphism as iso


class Isomorphisms(object):
    """
    Compare two storage graphs using the isomorphism concept.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def isomorphisms_iter(cls, graph1, graph2, node_match, edge_match):
        """
        Generator over isomorphisms on the graphs.

        :param graph1: a graph
        :param graph2: a graph
        :param node_match: a function that checks whether nodes are equal
        :type node_match: node * node -> bool
        :param edge_match: a function that checks whether edges are equal
        :type edge_match: node * node -> bool

        """
        matcher = iso.DiGraphMatcher(graph1, graph2, node_match, edge_match)
        return matcher.isomorphisms_iter()

    @classmethod
    def is_equivalent(cls, graph1, graph2, node_match, edge_match):
        """
        Whether these graphs represent equivalent storage configurations.

        :param graph1: a graph
        :param graph2: a graph
        :param node_match: a function that checks whether nodes are equal
        :type node_match: node * node -> bool
        :param edge_match: a function that checks whether edges are equal
        :type edge_match: node * node -> bool

        :returns: True if the graphs are equivalent, otherwise False
        :rtype: bool

        Note that two graphs are equivalent only if they possess an isomorphism
        in both directions.

        This can be checked cheaply by checking that both graphs have the same
        number of nodes.
        """
        if len(graph1) != len(graph2):
            return False
        iso_iter = cls.isomorphisms_iter(
           graph1,
           graph2,
           node_match,
           edge_match
        )
        return next(iso_iter, None) is not None
