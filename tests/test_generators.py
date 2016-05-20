# -*- coding: utf-8 -*-
# Copyright (C) 2016  Red Hat, Inc.
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
    tests.test_generators
    =====================

    Tests graph generators.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pydevDAG

from ._constants import GRAPH


class TestDepthFirst(object):
    """
    Test the depth first generator.
    """
    # pylint: disable=too-few-public-methods

    def test_depth_first(self):
        """
        Test that set of nodes encountered in traversal equals set in graph.
        """
        gen_nodes = list(pydevDAG.DepthFirst.nodes(GRAPH, lambda x: ''))
        assert frozenset(GRAPH.nodes()) == \
           frozenset(y for _, y, _ in gen_nodes)


class TestBreadthFirst(object):
    """
    Test the breadth first generator.
    """
    # pylint: disable=too-few-public-methods

    def test_breadth_first(self):
        """
        Test that set of nodes encountered in traversal equals set in graph.
        """
        gen_nodes = list(pydevDAG.BreadthFirst.nodes(GRAPH, lambda x: ''))
        assert frozenset(GRAPH.nodes()) == \
           frozenset(y for _, y, _ in gen_nodes)
