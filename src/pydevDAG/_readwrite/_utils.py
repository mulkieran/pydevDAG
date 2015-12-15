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
    pydevDAG._readwrite._utils
    ==========================

    Utilities for reading and writing.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io

import six


class StringUtils(object):
    """
    String related utilities.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def as_string(graph, write_func):
        """
        Return the entire graph as a single string in a structured format.

        :param `DiGraph` graph: the graph
        :param write_func: the function to write the graph
        :type write_func: `DiGraph` * file -> NoneType
        :returns: the graph as a stringlike thing
        """
        # pylint: disable=redefined-variable-type
        if six.PY2:
            output = io.BytesIO()
        else:
            output = io.StringIO()
        write_func(graph, output)
        return output.getvalue()

    @staticmethod
    def from_string(instr, read_func):
        """
        Get a graph from a string.

        :param read_func: a function that reads data from an input stream
        """
        # pylint: disable=redefined-variable-type
        if six.PY2:
            infile = io.BytesIO(instr.encode())
        else:
            infile = io.StringIO(instr)
        return read_func(infile)
