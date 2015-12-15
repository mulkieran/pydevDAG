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
    tests.test_traversal
    ====================

    Tests traversing the sysfs hierarchy.

    .. moduleauthor:: mulhern <amulhern@redhat.com>
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pydevDAG

import pytest

from hypothesis import given
from hypothesis import strategies
from hypothesis import Settings

from ._constants import BOTHS
from ._constants import CONTEXT
from ._constants import EITHERS
from ._constants import HOLDERS
from ._constants import SLAVES

NUM_TESTS = 5

# Use conditional to avoid processing tests if number of examples is too small.
# pytest.mark.skipif allows the test to be built, resulting in a hypothesis
# error if SLAVES or HOLDERS is empty.
if len(BOTHS) == 0:
    @pytest.mark.skipif(
       True,
       reason="no slaves or holders data for tests"
    )
    class TestTraversal(object):
        # pylint: disable=too-few-public-methods
        """
        An empty test class which is always skipped.
        """
        def test_dummy(self):
            """
            A dummy test, for which pytest can show a skip message.
            """
            pass
else:
    class TestTraversal(object):
        """
        A class for testing sysfs traversals.
        """
        @given(
           strategies.sampled_from(SLAVES),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_slaves(self, device):
            """
            Verify slaves do not contain originating device.
            """
            assert device not in pydevDAG.slaves(CONTEXT, device)

        @given(
           strategies.sampled_from(HOLDERS),
           settings=Settings(max_examples=NUM_TESTS)
        )
        def test_holders(self, device):
            """
            Verify holders do not contain originating device.
            """
            assert device not in pydevDAG.holders(CONTEXT, device)

        @given(
           strategies.sampled_from(EITHERS),
           strategies.booleans(),
           settings=Settings(max_examples=2 * NUM_TESTS)
        )
        def test_inverse(self, device, recursive):
            """
            Verify that a round-trip traversal will encounter the original
            device.

            :param device: the device to test
            :param bool recursive: if True, test recursive relationship

            If recursive is True, test ancestor/descendant relationship.
            If recursive is False, tests parent/child relationship.
            """
            # pylint: disable=too-many-function-args
            slaves = list(pydevDAG.slaves(CONTEXT, device, recursive))
            for slave in slaves:
                assert device in list(
                   pydevDAG.holders(CONTEXT, slave, recursive)
                )

            holders = list(pydevDAG.holders(CONTEXT, device, recursive))
            for holder in holders:
                assert device in list(
                   pydevDAG.slaves(CONTEXT, holder, recursive)
                )
