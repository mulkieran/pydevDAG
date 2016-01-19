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
    pydevDAG._attributes._edgetypes
    ===============================

    Types of graph edges.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from ._metaclasses import AttributeValue
from ._metaclasses import AttributeValues


@six.add_metaclass(abc.ABCMeta)
class EdgeType(AttributeValue):
    """
    Superclass of edge types.
    """
    # pylint: disable=too-few-public-methods
    pass

class Slave(EdgeType):
    """
    Encodes slaves/holders relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Slave = Slave() # pylint: disable=invalid-name

class Partition(EdgeType):
    """
    Encodes partition relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Partition = Partition() # pylint: disable=invalid-name

class Spindle(EdgeType):
    """
    Path to spindle relationship.
    """
    # pylint: disable=too-few-public-methods
    pass

Spindle = Spindle() # pylint: disable=invalid-name

class Congruence(EdgeType):
    """
    Congruence relationship between dm devices and partitions.
    """
    # pylint: disable=too-few-public-methods
    pass

Congruence = Congruence() # pylint: disable=invalid-name

class EnclosureBay(EdgeType):
    """
    Bay in an enclosure.
    """
    # pylint: disable=too-few-public-methods
    pass

EnclosureBay = EnclosureBay() # pylint: disable=invalid-name

class EdgeTypes(AttributeValues):
    """
    Enumeration of edge types.
    """
    # pylint: disable=too-few-public-methods
    SLAVE = Slave
    PARTITION = Partition
    SPINDLE = Spindle
    CONGRUENCE = Congruence
    ENCLOSUREBAY = EnclosureBay

    @classmethod
    def values(cls):
        return [
           cls.CONGRUENCE,
           cls.ENCLOSUREBAY,
           cls.PARTITION,
           cls.SLAVE,
           cls.SPINDLE
        ]
