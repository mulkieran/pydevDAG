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
    tests.test_utils
    ================

    Tests utilities.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

import pydevDAG

from ._constants import GRAPH

class TestGraphUtils(object):
    """
    Test utilities that work over networkx graphs.
    """
    # pylint: disable=too-few-public-methods

    def test_roots(self):
        """
        Verify that roots are really roots.
        """
        roots = pydevDAG.GraphUtils.get_roots(GRAPH)
        in_degrees = GRAPH.in_degree(roots)

        assert all(in_degrees[r] == 0 for r in roots)

    def test_set_direction(self):
        """
        Test setting direction results.
        """
        graph = pydevDAG.GraphUtils.set_direction(
           GRAPH,
           set_reversed=True,
           copy=True
        )
        assert graph.graph['reversed']

        graph = pydevDAG.GraphUtils.set_direction(
           graph,
           set_reversed=True,
           copy=False
        )
        assert graph.graph['reversed']


class TestDict(object):
    """
    Test setting and getting values in a dict.
    """
    # pylint: disable=too-few-public-methods

    @given(
        strategies.lists(elements=strategies.text(), max_size=7, min_size=1),
        strategies.integers()
    )
    @settings(max_examples=20)
    def test_set_and_get(self, keys, value):
        """
        Test basic getting and setting.
        """
        table = dict()
        with pytest.raises(pydevDAG.DAGError):
            pydevDAG.Dict.get_value(table, keys)

        if len(keys) > 1:
            with pytest.raises(pydevDAG.DAGError):
                pydevDAG.Dict.set_value(table, keys, value, force=False)


        pydevDAG.Dict.set_value(table, keys, value, force=True)
        assert pydevDAG.Dict.get_value(table, keys) == value

        pydevDAG.Dict.set_value(table, keys, value)
        assert pydevDAG.Dict.get_value(table, keys[:-1]) == {keys[-1]: value}

    def test_exceptions(self):
        """
        Test exceptions.
        """
        with pytest.raises(pydevDAG.DAGError):
            pydevDAG.Dict.set_value(dict(), [], True, force=False)
        with pytest.raises(pydevDAG.DAGError):
            pydevDAG.Dict.set_value(None, ['a'], True, force=False)
        with pytest.raises(pydevDAG.DAGError):
            pydevDAG.Dict.set_value(None, ['a'], True, force=False)
        with pytest.raises(pydevDAG.DAGError):
            pydevDAG.Dict.set_value(
               {'a': None},
               ['a', 'b', 'c'],
               True,
               force=False
            )

    def _build_table(self, keys, value=None):
        """
        Build a table to search.

        :param keys: a list of keys
        :type keys: list of text
        :param value: value to set at leaves
        :type value: object, None means this is a config dict
        """
        if keys == []:
            return value if value is not None else dict()

        if len(keys) == 1:
            return {keys[0]: value if value is not None else dict()}

        result = self._build_table(keys[2:], value)

        return {
           keys[0]: value if value is not None else dict(),
           keys[1]: ({'args': result} if value is None else result)
        }

    @given(
        strategies.lists(strategies.text()),
        strategies.integers()
    )
    @settings(max_examples=20)
    def test_get_values(self, keys, value):
        """
        Test getting and setting.

        First, set all leaves to ``value`` according to keys.

        Check that all values are found.
        """
        keys = list(set(keys))
        table = self._build_table(keys)
        tree = self._build_table(keys, value)
        result = list(pydevDAG.ExtendedLookup(table).get_values(tree))
        assert table == {} or (len(set(result)) == 1 and result[0] == value)

        unknown_key = '_' + ''.join(keys)
        with pytest.raises(pydevDAG.DAGError):
            list(pydevDAG.ExtendedLookup({unknown_key: {}}).get_values(tree))

    def test_get_values_simple(self):
        """
        Test what would be exceptions if an empty list did not sometimes
        mean the same thing.
        """
        assert list(pydevDAG.ExtendedLookup({}).get_values(None)) == []
