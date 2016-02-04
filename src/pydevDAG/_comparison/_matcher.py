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
    pydevDAG._comparison._matcher
    =============================

    Functions to compare nodes or edges for equality.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx

from .._attributes import ElementTypes


class Matcher(object):
    """
    Class with functions to match graph elements based on selected keys.

    Note that the keys must be at the top-level.
    """

    def __init__(self, keys, ele_type=ElementTypes.NODE):
        """
        Initializers.

        :param keys: list of keys to match
        :type keys: list of str
        :param ElementTypes ele_type: the type of a graph element
        """
        self._keys = keys
        self._ele_type = ele_type

    def get_match(self, graph1, graph2):
        """
        Returns a function that checks equality of two graph elements.

        :param keys: a list of keys whose values must be equal
        :types keys: list of str
        :param `DiGraph` graph1: a graph
        :param `DiGraph` graph2: a graph

        :returns: a function that compares two graph elements
        :rtype: ele * ele -> bool
        """
        attr_func = nx.get_node_attributes \
           if self._ele_type is ElementTypes.NODE \
           else nx.get_edge_attributes

        attr1_dict = dict()
        attr2_dict = dict()
        for key in self._keys:
            attr1_dict[key] = attr_func(graph1, key)
            attr2_dict[key] = attr_func(graph2, key)

        def the_func(ele1, ele2):
            """
            Checks equality of two elements.

            :param ele1: an element
            :param ele2: an element
            :returns: True if elements are equal, otherwise False
            :rtype: bool
            """
            node1_dict = dict((k, attr1_dict[k][ele1]) for k in self._keys)
            node2_dict = dict((k, attr2_dict[k][ele2]) for k in self._keys)
            return node1_dict == node2_dict

        return the_func

    def get_iso_match(self):
        """
        Get match function suitable for use with is_isomorphism method.

        :returns: a function that checks the equality of two graph elements
        :rtype: ele * ele -> bool
        """
        def the_func(attr1, attr2):
            """
            Checks equality of two elements.

            :param attr1: attributes of an element
            :param attr2: attributes of an element
            :returns: True if elements are equal, otherwise False
            :rtype: bool
            """
            dict_1 = dict((k, attr1[k]) for k in self._keys)
            dict_2 = dict((k, attr2[k]) for k in self._keys)
            return dict_1 == dict_2

        return the_func
