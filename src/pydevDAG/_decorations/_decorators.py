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
    pydevDAG._decorations._decorators
    =================================

    Tools to decorate networkx graphs in situ, i.e., as
    constructed rather than as read from a textual file.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class DifferenceMarkers(object):
    """
    Difference markers, either added or removed or present.
    """

    @staticmethod
    def node_differences(graph, difference, value):
        """
        Get node differences in ``graph`` based on ``difference``.

        :param `DiGraph` graph: the graph
        :param `DiGraph` difference: a graph representing the difference
        :param str value: marker to add to graph

        If node is in difference, adds ``value`` as "diffstatus" attribute.
        """
        ds_dict = dict()
        for node in graph:
            if node in difference:
                ds_dict[node] = value

        return {'diffstatus': ds_dict}

    @staticmethod
    def edge_differences(graph, difference, value):
        """
        Get edge differences in ``graph`` based on ``difference``.

        :param `DiGraph` graph: the graph
        :param `DiGraph` difference: a graph representing the difference
        :param str value: marker to add to graph

        If edge is in difference, adds ``value`` as "diffstatus" attribute.
        """
        ds_dict = dict()
        diff_edges = difference.edges()
        for edge in graph.edges_iter():
            if edge in diff_edges:
                ds_dict[edge] = value

        return {'diffstatus': ds_dict}
