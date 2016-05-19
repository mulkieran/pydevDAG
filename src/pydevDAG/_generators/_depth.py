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
    pydevDAG._generators._depth
    ===========================

    Do what amounts to a depth first traversal of the graph.

    .. moduleauthor::  Anne Mulhern  <amulhern@redhat.com>
"""

from .._utils import GraphUtils


class DepthFirst(object):
    """
    A depth-first traversal of the graph.
    """
    # pylint: disable=too-few-public-methods

    @classmethod
    def _nodes_recursive(cls, graph, key_func, node_info):
        """
        Recursively yield the nodes in depth-first search.

        :param DiGraph graph: the graph
        :param key_func: the key function for sorting
        :param node_info: the information about the node, depth and id
        :type node_info: tuple of str * int * bool

        The type yielded is tuple of str * int * bool
        """
        yield node_info

        (depth, node, _) = node_info

        next_depth = depth + 1
        successors = sorted(graph.successors(node), key=key_func)

        for succ in successors:
            infos = cls._nodes_recursive(
               graph,
               key_func,
               (next_depth, succ, succ is successors[-1])
            )
            for info in infos:
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
        for node in roots:
            infos = cls._nodes_recursive(
               graph,
               key_func,
               (0, node, node is roots[-1])
            )
            for info in infos:
                yield info
