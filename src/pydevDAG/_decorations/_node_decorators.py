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
    pydevDAG._decorations._node_decorators
    ======================================

    Tools to decorate networkx graphs in situ, i.e., as
    constructed rather than as read from a textual file.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

from itertools import groupby

import six

import pyudev

from parseudev import Devlink

from pydevDAG._attributes import NodeTypes

from pydevDAG._errors import DAGValueError


@six.add_metaclass(abc.ABCMeta)
class Domain(object):
    """
    A particular domain for decoration.

    A domain is just a particular way of going about gathering the information
    to use to decorate.

    All decoration objects in a particular domain require the same setup and
    will share the same interface.
    """

    @classmethod
    def name(cls):
        """
        The name of the domain.
        """
        return cls.__name__

    @abc.abstractmethod
    def decorate(self, node, attrdict): # pragma: no cover
        """
        Updates attributes on a node.

        :param str node: the node
        :param dict attrdict: dict of node attributes
        """
        raise NotImplementedError()


class Pyudev(Domain):
    """
    Construct functions for decorating using pyudev.
    """
    # pylint: disable=too-few-public-methods


    def __init__(self, objects):
        """
        Initializer.

        :param objects: a list of object that require a pyudev device
        """
        objects = list(objects)
        if any(o.DOMAIN is not self.__class__ for o in objects): # pragma: no cover
            raise DAGValueError('objects must be in this domain')

        self.objects = objects
        self.context = pyudev.Context()

    def decorate(self, node, attrdict):
        try:
            device = pyudev.Device.from_path(self.context, node)
        except pyudev.DeviceNotFoundError: # pragma: no cover
            return

        for obj in self.objects:
            if obj.decoratable(attrdict):
                obj.decorate(device, attrdict)


@six.add_metaclass(abc.ABCMeta)
class PyudevDecorator(object):
    """
    Defines interface of objects that use pyudev to do their decorating.
    """
    DOMAIN = Pyudev

    def decoratable(self, attrdict):
        """
        Whether ``attrdict`` represents a decoratable node.

        :param dict attrdict: dict of node attributes
        :returns: True if the node can be decorated by this class, else False
        :rtype: bool
        """
        # pylint: disable=no-self-use
        return attrdict['nodetype'] is NodeTypes.DEVICE_PATH

    @abc.abstractmethod
    def decorate(self, device, attrdict): # pragma: no cover
        """
        Decorate the ``attrdict`` belonging to ``device``.

        :param Device device: libudev device
        :param dict attrdict: currently stored dict for attributes
        """
        raise NotImplementedError()


class DevlinkValues(PyudevDecorator):
    """
    Add the informational part of device links to the graph.
    """

    def __init__(self, args):
        self.categories = args

    def decorate(self, device, attrdict):
        def key_func(link):
            """
            :returns: category of link, or "" if no category
            :rtype: str
            """
            key = link.category
            return key if key is not None else ""

        result = dict.fromkeys(self.categories)

        # pylint: disable=protected-access
        devlinks = sorted(
           (Devlink(d) for d in device.device_links),
           key=key_func
        )
        result.update(
           (k, g) for (k, g) in groupby(devlinks, key_func) if \
               k in self.categories
        )

        attrdict['DEVLINK'] = result


class SysfsAttributes(PyudevDecorator):
    """
    Find sysfs attributes for the device nodes of a network graph.

    Set a value for every name requested.
    """

    def __init__(self, args):
        self.names = args

    def decorate(self, device, attrdict):
        attributes = device.attributes

        res = dict()
        for key in self.names:
            try:
                res[key] = attributes.asstring(key)
            except (KeyError, UnicodeDecodeError): # pragma: no cover
                res[key] = None
        attrdict['SYSFS'] = res


class Sysname(PyudevDecorator):
    """
    Get the sysname for the object.
    """

    def __init__(self, args):
        pass

    def decorate(self, device, attrdict):
        attrdict['SYSNAME'] = device.sys_name


class UdevProperties(PyudevDecorator):
    """
    Find udev properties for the device nodes of a network graph.

    Set a value for every name requested.
    """

    def __init__(self, args):
        self.names = args

    def decorate(self, device, attrdict):
        attrdict['UDEV'] = \
           dict((k, device.get(k)) for k in self.names)


class NodeDecorator(object):
    """
    A node decorator for a particular configuration.
    """

    _FUNCTIONS = {
       'DEVLINK' : DevlinkValues,
       'SYSNAME': Sysname,
       'SYSFS': SysfsAttributes,
       'UDEV': UdevProperties
    }

    def __init__(self, config):
        """
        Initializer.

        :param config: configuration for node decorators
        :type config: dict (JSON)
        """
        # list of tuple of NodeType * dict
        nodeconfigs = (
           (NodeTypes.get_value(k), v) for (k, v) in config.items()
        )
        configs = [(k, v) for (k, v) in nodeconfigs if k is not None]

        # map of NodeType * (list of Domain)
        self.table = dict((k, self.get_decorator(v)) for (k, v) in configs)

    def get_decorator(self, config):
        """
        Get a decorator for one particular nodetype.

        :param config: the configuration for a particular node type
        :type config: dict (JSON)

        :returns: a sequence of objects for decorating
        :rtype: list of Domain
        """
        # Find all available classes for a given key
        # list of tuple of type * dict (JSON)
        klasses = [(self._FUNCTIONS.get(k), v) for (k, v) in config.items()]

        # sort the objects by their domain
        key_func = lambda x: x.DOMAIN
        sort_func = lambda x: key_func(x).name()
        objects = groupby(
           sorted(
               [k(v.get('args')) for (k, v) in klasses if k is not None],
               key=sort_func
           ),
           key_func
        )

        # construct a domain object from its component objects
        return [k(v) for (k, v) in objects]

    def decorate(self, node, attrdict):
        """
        Decorates ``attrdict`` with additional attributes.

        :param Context context: a pyudev context
        :param str node: the node
        :param dict attrdict: dict of node attributes
        """
        objects = self.table.get(attrdict['nodetype'])
        if objects is not None:
            for obj in  objects:
                obj.decorate(node, attrdict)
