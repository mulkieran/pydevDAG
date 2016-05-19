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
    tests.test_readwrite
    ====================

    Tests reading and writing of graph.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

import networkx.algorithms.isomorphism as iso

import pydevDAG

from ._constants import DECORATED

class TestStringUtils(object):
    """
    Test utilities that work over networkx graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_as_string(self):
        """
        Verify non-empty string.
        """
        assert pydevDAG.StringUtils.as_string(DECORATED, pydevDAG.Writer.write)

    def test_from_string(self):
        """
        Verify succesful reading of empty graph.
        """
        strinput = \
           '{"directed": true, "graph" : [], "nodes" : [], "links" : []}'
        res = pydevDAG.StringUtils.from_string(strinput, pydevDAG.Reader.read)
        assert isinstance(res, nx.DiGraph)
        assert len(res) == 0

    def test_inverses(self):
        """
        Test that writing the string and then reading it yields identical graph.
        """

        val = pydevDAG.StringUtils.as_string(DECORATED, pydevDAG.Writer.write)
        res = pydevDAG.StringUtils.from_string(val, pydevDAG.Reader.read)
        assert iso.is_isomorphic(
           DECORATED,
           res,
           lambda x, y: x == y,
           lambda x, y: x == y
        )


class TestRewriter(object):
    """
    Test rewriting of a graph.
    """
    # pylint: disable=too-few-public-methods

    def test_inverses(self):
        """
        Verify that destringize inverts stringize.
        """
        identical = lambda x, y: x == y
        copied = DECORATED.copy()
        assert iso.is_isomorphic(copied, DECORATED, identical, identical)
        pydevDAG.Rewriter.stringize(copied)
        assert not iso.is_isomorphic(copied, DECORATED, identical, identical)
        pydevDAG.Rewriter.destringize(copied)
        assert iso.is_isomorphic(copied, DECORATED, identical, identical)
