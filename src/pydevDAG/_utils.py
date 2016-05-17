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

import networkx as nx

from ._errors import DAGValueError


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

    @staticmethod
    def reverse(graph, copy=True):
        """
        Reverse a graph and indicate its status.

        :param `DiGraph` graph: the graph
        :param bool copy: if True, make a new copy of the graph
        :returns: a reversed graph
        :rtype: `DiGraph`
        """
        key = 'reversed'
        graph = graph.reverse(copy=copy)
        try:
            graph.graph[key] = not graph.graph[key]
        except KeyError:
            graph.graph[key] = True
        return graph

    @classmethod
    def set_direction(cls, graph, set_reversed=False, copy=True):
        """
        Set a graph's direction.

        :param `DiGraph` graph: the graph
        :param bool set_reversed: if True, direction is reversed
        :param bool copy: if True, make a new copy of the graph
        :returns: a reversed graph
        :rtype: `DiGraph`
        """
        try:
            is_reversed = graph.graph['reversed']
        except KeyError:
            is_reversed = False

        if set_reversed != is_reversed:
            graph = cls.reverse(graph, copy=copy)

        return graph


class Dict(object):
    """
    Set or get the values of objects located in arbitrarily nested dicts.
    """

    @staticmethod
    def get_value(tree, keys):
        """
        Get value.

        :param dict tree: arbitrarily nested dict
        :param keys: list of keys
        :type keys: list of str
        :returns: the result of traversing ``tree`` by means of ``keys``
        :rtype: object

        :raises DAGValueError: if the value can not be found
        """
        result = tree
        for key in keys:
            try:
                result = result[key]
            except (KeyError, TypeError):
                raise DAGValueError("value for sequence %s not found" % keys)
        return result

    @staticmethod
    def set_value(tree, keys, value, force=False):
        """
        Set value.

        :param dict tree: arbitrarily nested dict
        :param keys: list of keys
        :type keys: list of str
        :param object value: the value to set
        :param bool force: if True, make new empty dict entries if lookup fails

        :raises DAGValueError: on bad parameters

        Bad parameters are considered to have been passed if:
        * An empty list of keys, don't know what to set.
        * A prefix of the list yields a non-dict value.
        """
        if keys == []:
            raise DAGValueError()
        (first, last) = (keys[:-1], keys[-1])

        lvalue = tree
        for key in first:
            try:
                if key not in lvalue:
                    if force:
                        lvalue[key] = dict()
                    else:
                        raise DAGValueError()
            except TypeError:
                raise DAGValueError()
            lvalue = lvalue[key]

        try:
            lvalue[last] = value
        except TypeError:
            raise DAGValueError()


class ExtendedLookup(object):
    """
    Get the result of looking at multiple attributes of a node at once.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, config):
        """
        Initializer.

        :param config: the config
        :type config: dict(JSON)
        """
        self.config = config

    def get_values(self, tree):
        """
        Generate values for keys.

        :param dict tree: arbitrarily nested dict

        Yields in sequence, the values for each key, None if no value found.
        """
        if self.config == {}:
            return
        for val in self._get_values(tree, self.config):
            yield val

    def _get_values(self, tree, config):
        """
        Generate values for keys.

        :param dict tree: arbitrarily nested dict
        :param config: the config
        :type config: dict (JSON)
        :raises DAGValueError: if any key not found
        """
        if config is None:
            yield tree
            return

        for (key, val) in config.items():
            try:
                subtree = tree[key]
            except (AttributeError, KeyError, TypeError):
                raise DAGValueError('no key %s in tree' % key)
            else:
                for rval in self._get_values(subtree, val.get('args')):
                    yield rval
