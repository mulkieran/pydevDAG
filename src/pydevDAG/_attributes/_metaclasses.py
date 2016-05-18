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
    pydevDAG._metaclasses
    =====================

    Metaclasses for graph attributes.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

@six.add_metaclass(abc.ABCMeta)
class AttributeValue(object):
    """
    Abstract class that represents some attribute constant.
    """
    # pylint: disable=too-few-public-methods
    def __str__(self): # pragma: no cover
        return self.__class__.__name__

    def __repr__(self): # pragma: no cover
        return "%s()" % str(self)

    def __deepcopy__(self, memo):
        # pylint: disable=unused-argument
        return self

    def __copy__(self): # pragma: no cover
        return self

@six.add_metaclass(abc.ABCMeta)
class AttributeValues(object):
    """
    Some set of values for a graph attribute.
    """

    @classmethod
    @abc.abstractmethod
    def values(cls):
        """
        Return a list of the values in the class.
        """
        raise NotImplementedError() # pragma: no cover

    @classmethod
    def get_value(cls, name):
        """
        Return the object corresponding to ``name``.

        :returns: the type object that matches ``name`` or None
        :rtype: `NodeType` or NoneType
        """
        return next((obj for obj in cls.values() if str(obj) == name), None)
