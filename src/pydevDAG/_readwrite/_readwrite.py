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
    pydevDAG._readwrite._readwrite
    ==============================

    Tools to write out a graph or read one in.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import json

from networkx.readwrite import json_graph

from ._write import Rewriter


class JSONWriter(object):
    """
    Write graph to a file.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def write(graph, out):
        """
        Write a graph to an output stream.

        :param DiGraph graph: a graph
        :param out: an output stream
        """
        graph = graph.copy()
        Rewriter.stringize(graph)
        data = json_graph.node_link_data(graph)
        json.dump(data, out, indent=4)
        print(end=os.linesep, file=out)


class JSONReader(object):
    """
    Read graph from a file.
    """

    @staticmethod
    def readin(data):
        """
        Read data from a string input.

        :param data: the JSON formatted data
        :returns: the graph
        :rtype: DiGraph
        """
        graph = json_graph.node_link_graph(data)
        Rewriter.destringize(graph)
        return graph

    @classmethod
    def read(cls, instream):
        """
        Read a graph from an input stream

        :param instream: the input stream
        :returns: a graph corresponding to the JSON data in the stream
        """
        data = json.load(instream)
        return cls.readin(data)

Reader = JSONReader
Writer = JSONWriter
