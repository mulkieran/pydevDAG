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
    pydevDAG._print._mapping
    ========================

    Prints a mapping between graph nodes.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pydevDAG._utils import GeneralUtils


class MapLineInfos(object):
    """
    Class that generates info for every line of a mapping.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, graph1, graph2, getters, keys):
        """
        Initializer.

        :param DiGraph graph1: the first graph
        :param DiGraph graph1: the second graph
        :param getters: classes to get values to print
        :type getters: list of type
        :param keys: keys for column headers
        :type keys: tuple of str * str
        """
        self._graph1 = graph1
        self._graph2 = graph2

        self._func = GeneralUtils.composer([g.getter for g in getters])

        self.keys = keys

    def info(self, mapping):
        """
        Get the info for the given mapping.
        :param mapping: mapping from nodes in graph1 to nodes in graph2
        :type mapping: dict of node * node
        :returns: info for left and right sides, sorted by left-side value
        :rtype: dict of (str or NoneType)
        """
        lkey, rkey = self.keys
        lines = (
           {
              lkey : self._func(self._graph1.node[left]),
              rkey : self._func(self._graph2.node[right])
           } for (left, right) in mapping.items()
        )
        return sorted(list(lines), key=lambda x: x[lkey])
