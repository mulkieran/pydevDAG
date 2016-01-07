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
    pydevDAG._structure._pyudev
    ===========================

    Tools to build and manipulate graphs of device relationships
    discovered using pyudev.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import networkx as nx


class PyudevAggregateGraph(object):
    """
    Build a graph according to specifications.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def graph(context, name, classes):
        """
        Build a graph using the designated classes.

        :param context: a context
        :param str name: a name for the graph
        :param classes: a list of graph classes
        :type classes: list of type, each type must be subtype of PyudevGraph
        :returns: a graph
        :rtype: nx.DiGraph
        """
        return nx.compose_all(
            (t.complete(context) for t in classes),
            name=name
        )
