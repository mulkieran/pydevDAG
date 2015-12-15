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
    pydevDAG.traversal
    ==================

    Traversing the sysfs hierarchy.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
import os

from pyudev.device import Device

__all__ = ['topology_walk', 'slaves', 'holders']

def topology_walk(top, follow_slaves=True, recursive=True):
    """
    Walk the sysfs directory in depth first search,
    yielding directories corresponding to devices in sysfs.

    :param str top: directory to begin at
    :param bool follow_slaves: if True, follow slaves, otherwise, holders
    :param bool recursive: if False, only show one level

    ``top`` itself is not in the result.
    """
    link_dir = os.path.join(top, 'slaves' if follow_slaves else 'holders')

    if os.path.isdir(link_dir):
        names = os.listdir(link_dir)
        files = (os.path.abspath(os.path.join(link_dir, f)) for f in names)
        links = (os.readlink(f) for f in files if os.path.islink(f))
        devs = (os.path.normpath(os.path.join(link_dir, l)) for l in links)
        for dev in devs:
            if recursive:
                for res in topology_walk(dev, follow_slaves):
                    yield res
            yield dev

def device_wrapper(func):
    """ Wraps function so that it returns Device rather than directory. """

    @functools.wraps(func)
    def new_func(context, device, recursive=True):
        """
        New function wraps yielded value in Device.

        :param `Context` context: udev context
        :param `Device` device: device to start from
        :param bool recursive: if False, only show immediate slaves
        """
        for directory in func(device.sys_path, recursive):
            yield Device.from_sys_path(context, directory)

    return new_func

@device_wrapper
def slaves(device, recursive=True):
    """
    Yield slaves of ``device``.

    :param `Context` context: udev context
    :param `Device` device: device to start from
    :param bool recursive: if False, only show immediate slaves

    :returns: topology walk generator specialized for slaves
    """
    return topology_walk(device, True, recursive)

@device_wrapper
def holders(device, recursive=True):
    """
    Yield holders of ``device``.

    :param `Context` context: udev context
    :param `Device` device: device to start from
    :param bool recursive: if False, only show immediate holders

    :returns: topology walk generator specialized for holders
    """
    return topology_walk(device, False, recursive)
