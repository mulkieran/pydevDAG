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
    tests.constants
    ===============

    Constants for testing.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pyudev

import pydevDAG

CONTEXT = pyudev.Context()
DEVICES = CONTEXT.list_devices()

# pylint: disable=too-many-function-args

SLAVES = [d for d in DEVICES if list(pydevDAG.slaves(CONTEXT, d, False))]

HOLDERS = [d for d in DEVICES if list(pydevDAG.holders(CONTEXT, d, False))]

BOTHS = list(set(SLAVES).intersection(set(HOLDERS)))

EITHERS = list(set(SLAVES).union(set(HOLDERS)))

GRAPH = pydevDAG.GenerateGraph.get_graph(CONTEXT, "graph")

DECORATED = pydevDAG.GenerateGraph.get_graph(CONTEXT, "graph")
pydevDAG.GenerateGraph.decorate_graph(DECORATED)
