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
    pydevDAG._print._utils
    ======================

    Utilities for textual display.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx


class HelpersUtils(object):
    """
    Utilities for print helpers.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def get_map(getters, graph):
        """
        Build a map for graph for requires.

        :param getters: an iterable of NodeGetter classes
        :param graph: a networkx graph to use to obtain the map.
        :type graph: DiGraph

        :returns: a dictionary with requires as keys
        :rtype: dict of str * (dict of node * object)

        The keys of the dictionary are the required fields.
        Each value is a dictionary from node to value for the field.
        """
        requires = set(r for g in getters for r in g.map_requires)
        return dict((r, nx.get_node_attributes(graph, r)) for r in requires)
