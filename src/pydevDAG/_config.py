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
    pydevDAG._config
    ================

    Handling configuration information.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from ._errors import DAGValueError


class _Config(object):
    """
    Handle external configuration information.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, path):
        """
        Initializer.

        :param str path: the path of the configuration file

        :raises DAGError: on unusable path
        """
        try:
            with open(path) as instream:
                self.config = json.load(instream)
        except (ValueError, EnvironmentError) as err: # pragma: no cover
            raise DAGValueError(err)

    def get_node_decoration_spec(self):
        """
        Get the specification regarding the decoration of nodes.

        :returns: the specification for node decoration
        :rtype: dict or str
        """
        return self.config['nodedecorations']

    def get_graph_type_spec(self):
        """
        Get specification about the structure of the graph.

        :returns: the kinds of graphs that make up the whole graph
        :rtype: dict of str
        """
        return self.config['graph_types']
