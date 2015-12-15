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
    pydevDAG._print._helpers
    ========================

    Little snippets of code to print stuff.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

import bytesize

from pydevDAG._attributes import DiffStatuses

@six.add_metaclass(abc.ABCMeta)
class NodeGetter(object):
    """
    Abstract parent class of classes for getting string info for a column.
    """
    # pylint: disable=too-few-public-methods

    map_requires = abc.abstractproperty(
       doc="maps to get using get_node_attributes"
    )

    @staticmethod
    @abc.abstractmethod
    def getter(maps):
        """
        Get a function that obtains a string from a node.

        :param maps: a dict of maps from nodes to attribute values
        :type maps: dict of str * (dict of node * object)
        :returns: a function that takes a node and returns a string
        :rtype: node -> (str or NoneType)
        """
        raise NotImplementedError()

class ByPath(NodeGetter):
    """
    Get the value of the path devlink for the node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['DEVLINK']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates a by-path value.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            info = maps['DEVLINK'].get(node)
            if info is None:
                return None

            links = info.get('by-path')
            if links is None:
                return None

            return "; ".join(str(link.value) for link in links)

        return the_func

class Devname(NodeGetter):
    """
    Get a name for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['UDEV']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates a DEVNAME or identifier.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            udev_info = maps['UDEV'].get(node)
            return udev_info and udev_info.get('DEVNAME')

        return the_func

class Devpath(NodeGetter):
    """
    Get a name for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['UDEV']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates a DEVPATH or identifier.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            udev_info = maps['UDEV'].get(node)
            return udev_info and udev_info.get('DEVPATH')

        return the_func

class Devtype(NodeGetter):
    """
    Get a device type for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['UDEV']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates a DEVTYPE.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            udev_info = maps['UDEV'].get(node)
            return udev_info and udev_info.get('DEVTYPE')

        return the_func


class Diffstatus(NodeGetter):
    """
    Get a diffstatus for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['diffstatus']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates the diffstatus.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            diffstatus = maps['diffstatus'].get(node)
            if diffstatus is DiffStatuses.ADDED:
                return 'ADDED'
            if diffstatus is DiffStatuses.REMOVED:
                return 'REMOVED'
            return None

        return the_func


class Dmname(NodeGetter):
    """
    Get a size for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['SYSFS']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates the dm-name.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            sysfs = maps['SYSFS'].get(node)
            if sysfs is None:
                return None
            return sysfs.get('dm/name')

        return the_func


class Identifier(NodeGetter):
    """
    Get a name for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['identifier']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates an identifier.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            return maps['identifier'][node]

        return the_func


class Size(NodeGetter):
    """
    Get a size for a node.
    """
    # pylint: disable=too-few-public-methods

    map_requires = ['SYSFS']

    @staticmethod
    def getter(maps):

        def the_func(node):
            """
            Calculates the size.

            :param node: the node
            :returns: the value to display for ``node``
            :rtype: str or NoneType
            """
            sysfs = maps['SYSFS'].get(node)
            if sysfs is None:
                return None
            size = sysfs.get('size')
            if size is not None:
                return str(bytesize.Size(size, bytesize.Size(512)))
            else:
                return None

        return the_func


class NodeGetters(object):
    """
    Class for managing NodeGetters.
    """
    # pylint: disable=too-few-public-methods

    BY_PATH = ByPath
    DEVNAME = Devname
    DEVPATH = Devpath
    DEVTYPE = Devtype
    DIFFSTATUS = Diffstatus
    DMNAME = Dmname
    IDENTIFIER = Identifier
    SIZE = Size
