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
    pydevDAG._utils
    ===============

    Generic utilities.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools

import networkx as nx


class GraphUtils(object):
    """
    Generic utilties for graphs.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def get_roots(graph):
        """
        Get the roots of a graph.

        :param `DiGraph` graph: the graph

        :returns: the roots of the graph
        :rtype: list of `Node`
        """
        return [n for n in graph if not nx.ancestors(graph, n)]


class SortingUtils(object):
    """
    Utilities helpful for sorting.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def str_key_func_gen(func):
        """
        A wrapper function that generates a function that yields a str
        for all values.

        :param func: a function that yields a result when applied to an arg
        :type func: 'a -> *
        """

        @functools.wraps(func)
        def key_func(value):
            """
            Transforms the result of func to a str type if it is not already.
            None becomes '', so that its value will appear first, all other
            non-str values are converted to str.

            :param `a value: a value to pass to func
            """
            res = func(value)
            return '' if res is None else str(res)

        return key_func
