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
    pydevDAG._generators._breadth
    =============================

    Do what amounts to a breadth first traversal of the graph.

    .. moduleauthor::  Anne Mulhern  <amulhern@redhat.com>
"""

from collections import deque

from .._utils import GraphUtils


class BreadthFirst(object):
    """
    A depth-first traversal of the graph.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def breadth_first(cls, graph, key_func, nodeinfos):
        """
        Do a breadth first search from nodes.

        :param DiGraph graph: the graph
        :param key_func: key function for sorting
        :type key_func: str -> object
        :param nodeinfos: the node infos to start from
        :type nodeinfos: deque of tuple of int * str * bool
        """
        while len(nodeinfos) != 0:
            info = nodeinfos.popleft()
            (depth, node, _) = info
            successors = sorted(graph.successors(node), key=key_func)
            nodeinfos.extend(
               (depth + 1, s, s is successors[-1]) for s in successors
            )
            yield info

    @classmethod
    def nodes(cls, graph, key_func):
        """
        Yield the nodes in order, along with their depth.

        :param DiGraph graph: the graph, with nodes
        :param key_func: key function to allow sorting of nodes
        :type key_func: str -> object

        Each returned value has type tuple of node * int.
        """
        roots = sorted(GraphUtils.get_roots(graph), key=key_func)
        return cls.breadth_first(
           graph,
           key_func,
           deque((0, r, r is roots[-1]) for r in roots)
        )
