# -*- coding: utf-8 -*-
# Copyright (C) 2016  Red Hat, Inc.
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
    pydevDAG._queries._process
    ==========================

    Process a query into HTML.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import pystache

from .._errors import DAGValueError

from ._enclosures import ByEnclosures


class ProcessQuery(object):
    """
    Process a query on a graph rendering the result as HTML.
    """

    _TABLE = {
       'BY_ENCLOSURES' : (ByEnclosures, 'enclosures.mustache'),
    }

    @classmethod
    def keys(cls):
        """
        Keys for queries.

        :returns: a sequence of valid keys
        :rtype: list
        """
        return list(cls._TABLE.keys())

    @classmethod
    def process(cls, graph, query_type):
        """
        Process the query.

        :param DiGraph graph: the graph
        :param query_type: the type of query
        :type query_type: an element in keys()
        """
        if query_type not in cls.keys():
            raise DAGValueError('query_type must be among keys()')

        (klass, template_name) = cls._TABLE[query_type]
        result = klass.get(graph)
        template_path = os.path.normpath(
           os.path.join(
              os.path.dirname(__file__),
              '../data/html',
              template_name
           )
        )
        with open(template_path, 'r') as instream:
            template = instream.read()
        parsed = pystache.parse(template.decode())
        return pystache.Renderer().render(parsed, result)
