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
    pydevDAG._print._print
    ======================

    Textual display of graph.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools


class Print(object):
    """
    Methods to print a list of lines as a table.
    """

    @staticmethod
    def calculate_widths(column_headers, lines, padding):
        """
        Calculate widths of every column.

        :param column_headers: column headers
        :type column_headers: list of str
        :param lines: line infos
        :type lines: list of dict
        :param int padding: number of spaces to pad on right

        :returns: a table of key/length pairs
        :rtype: dict of str * int
        """
        widths = functools.reduce(
           lambda d, l: dict((k, max(len(l[k]), d[k])) for k in l),
           lines,
           dict((k, len(k)) for k in column_headers)
        )

        return dict((k, widths[k] + padding) for k in widths)

    @staticmethod
    def header_str(column_widths, column_headers, alignment):
        """
        Get the column headers.

        :param column_widths: map of widths of each column
        :type column_widths: dict of str * int
        :param column_headers: column headers
        :type column_headers: list of str
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}

        :returns: the column headers
        :rtype: str
        """
        format_str = "".join(
           '{:%s%d}' % (alignment[k], column_widths[k]) for k in column_headers
        )
        return format_str.format(*column_headers)

    @staticmethod
    def format_str(column_widths, column_headers, alignment):
        """
        Format string for every data value.

        :param column_widths: map of widths of each column
        :type column_widths: dict of str * int
        :param column_headers: column headers
        :type column_headers: list of str
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}

        :returns: a format string
        :rtype: str
        """
        return "".join(
           '{%s:%s%d}' % (k, alignment[k], column_widths[k]) \
              for k in column_headers
        )

    @classmethod
    def lines(cls, column_headers, lines, padding, alignment):
        """
        Yield lines to be printed.

        :param column_headers: column headers
        :type column_headers: list of str
        :param lines: line infos
        :type lines: list of dict
        :param int padding: number of spaces to pad on right
        :param alignment: alignment for column headers
        :type alignment: dict of str * str {'<', '>', '^'}
        """
        column_widths = cls.calculate_widths(column_headers, lines, padding)

        yield cls.header_str(column_widths, column_headers, alignment)

        fmt_str = cls.format_str(column_widths, column_headers, alignment)
        for line in lines:
            yield fmt_str.format(**line)
