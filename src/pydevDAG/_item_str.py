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
    pydevDAG._item_str
    ========================

    Little snippets of code to yield values associated with a node.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

import justbytes

import parseudev

from ._attributes import NodeTypes
from ._errors import DAGValueError
from ._utils import Dict


@six.add_metaclass(abc.ABCMeta)
class NodeGetter(object):
    """
    Abstract parent class of classes for getting string info for a column.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    @abc.abstractmethod
    def getter(node):
        """
        Get a function that obtains a string from a node.

        :param dict node: the attributes of the node
        :returns: a value for this node
        :rtype: object
        """
        raise NotImplementedError()


class ByPath(NodeGetter):
    """
    Get the value of the path devlink for the node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            links = Dict.get_value(node, ['DEVLINK', 'by-path'])
            if links is None:
                return None
            else:
                return "; ".join(str(link.value) for link in links)
        except DAGValueError:
            return None


class Devname(NodeGetter):
    """
    Get a name for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'DEVNAME'])
        except DAGValueError:
            return None


class Devpath(NodeGetter):
    """
    Get a name for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'DEVPATH'])
        except DAGValueError:
            return None


class Devtype(NodeGetter):
    """
    Get a device type for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'DEVTYPE'])
        except DAGValueError:
            return None


class Dmname(NodeGetter):
    """
    Get a size for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'DM_NAME'])
        except DAGValueError:
            return None


class DmUuidSubsystem(NodeGetter):
    """
    Get the subsystem prefix from the DM_UUID.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            dmuuid = Dict.get_value(node, ['UDEV', 'DM_UUID'])
            if dmuuid is None:
                return None
            match_dict = parseudev.DMUUIDParse().parse(dmuuid)
            return match_dict.get('subsystem')
        except DAGValueError:
            return None


class Identifier(NodeGetter):
    """
    Get a name for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        return Dict.get_value(node, ['identifier'])


class IdPath(NodeGetter):
    """
    Get an ID_PATH value for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'ID_PATH'])
        except DAGValueError:
            return None


class IdSasPath(NodeGetter):
    """
    Get an ID_SAS_PATH value for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'ID_SAS_PATH'])
        except DAGValueError:
            return None


class NodeType(NodeGetter):
    """
    Get the type of the node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        nodetype = node['nodetype']
        if nodetype == NodeTypes.WWN:
            return "Drive"
        elif nodetype == NodeTypes.DEVICE_PATH:
            return 'Device'
        else:
            return None


class Size(NodeGetter):
    """
    Get a size for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            size = Dict.get_value(node, ['SYSFS', 'size'])
            if size is None:
                return None
            else:
                return str(justbytes.Range(size, justbytes.Range(512)))
        except DAGValueError:
            return None


class Subsystem(NodeGetter):
    """
    Get a SUBSYSTEM value for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['UDEV', 'SUBSYSTEM'])
        except DAGValueError:
            return None


class Sysname(NodeGetter):
    """
    Get a sysname value for a node.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def getter(node):
        try:
            return Dict.get_value(node, ['SYSNAME'])
        except DAGValueError:
            return None


class NodeGetters(object):
    """
    Class for managing NodeGetters.
    """
    # pylint: disable=too-few-public-methods

    BY_PATH = ByPath # may be deprecated
    DEVNAME = Devname
    DEVPATH = Devpath
    DEVTYPE = Devtype
    DMNAME = Dmname
    DMUUIDSUBSYSTEM = DmUuidSubsystem
    IDENTIFIER = Identifier
    IDPATH = IdPath
    IDSASPATH = IdSasPath
    NODETYPE = NodeType
    SIZE = Size
    SUBSYSTEM = Subsystem
    SYSNAME = Sysname
