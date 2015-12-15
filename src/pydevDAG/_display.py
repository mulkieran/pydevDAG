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
    pydevDAG._display
    =================

    Tools to display graphs of various kinds.

    .. moduleauthor::  mulhern <amulhern@redhat.com>
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import os

from functools import reduce # pylint: disable=redefined-builtin

import six

from ._attributes import DiffStatuses
from ._attributes import EdgeTypes
from ._attributes import NodeTypes

class HTMLUtils(object):
    """
    A class to handle HTML generation for HTML-style labels.
    """

    @staticmethod
    def make_table(rows):
        """
        Make an HTML table from a list of rows.

        :param rows: a list of rows as <td>...</td> strings
        :type rows: list of str
        :returns: HTML sring designating a table
        :rtype: str
        """
        table_attributes = "border=\"0\" cellborder=\"1\" cellspacing=\"0\""
        row_str = reduce(lambda x, y: x + y, rows, "")
        return "<table %s>%s</table>" % (table_attributes, row_str)

    @staticmethod
    def set_html_label(node, label):
        """
        Set an html label on a node.

        :param `Node` node: the node
        :param str label: the label
        """
        node.attr['label'] = "<%s>" % label
        node.attr['shape'] = 'none'


class Utils(object):
    """
    General utilities for graph transformations.
    """

    @staticmethod
    def copy_attr(attr):
        """
        Copy attr object to a dict of keys and values.

        :param attr: the attributes oject
        :returns: a dict of attributes
        :rtype: dict
        """
        return dict([(k, attr[k]) for k in attr])

    @staticmethod
    def get_attr(ele, keys):
        """
        Resolve the value of ``keys`` on ``ele``.

        Since any nested values end up as simple strings, need to evaluate
        the resulting string to get an actual dict.

        :param ele: a graph element
        :type ele: a `Node` or `Edge`
        :param keys: a list of keys
        :type keys: list of str
        :returns: the result of reading from the nested dicts or None
        :rtype: str or NoneType
        """
        res = ele.attr[keys[0]]
        if len(keys) == 1:
            return res

        return reduce(
           lambda x, y: x and x.get(y),
           keys[1:],
           eval(res) # pylint: disable=eval-used
        )

    @staticmethod
    def is_node_type(node, node_type):
        """
        Whether ``node`` has type ``node_type``.

        :param `agraph.Edge` node: the node
        :param `EdgeType` node_type: an node type
        :returns: True if ``node`` has type ``node_type``, otherwise False
        :rtype: bool
        """
        return node.attr['nodetype'] == str(node_type)

    @staticmethod
    def is_edge_type(edge, edge_type):
        """
        Whether ``edge`` has type ``edge_type``.

        :param `agraph.Edge` edge: the edge
        :param `EdgeType` edge_type: an edge type
        :returns: True if ``edge`` has type ``edge_type``, otherwise False
        :rtype: bool
        """
        return edge.attr['edgetype'] == str(edge_type)

    @staticmethod
    def is_diff_status(ele, diff_status):
        """
        Whether ``ele`` has diff status ``diff_status``.

        :param ele: the graph element
        :type edge: `agraph.Edge` or `agraph.Node`
        :returns: True if ``ele`` has status ``diff_status``, otherwise False
        :rtype: bool
        """
        return ele.attr['diffstatus'] == str(diff_status)

@six.add_metaclass(abc.ABCMeta)
class GraphTransformer(object):
    """
    Abstract superclass of graph transformers.
    """

    @staticmethod
    @abc.abstractmethod
    def xform_object(graph, obj):
        """
        Transform ``obj``.

        :param `AGraph` graph: the graph
        :param obj: the object to transform
        """
        raise NotImplementedError()


    @classmethod
    @abc.abstractmethod
    def objects(cls, graph):
        """
        Locate the objects to transform.

        :param `AGraph` graph: the graph
        :returns: an iterable of objects
        :rtype: iterable
        """
        raise NotImplementedError()


    @classmethod
    def xform(cls, graph):
        """
        Do the transformation.

        :param `AGraph` graph: the graph
        """
        for obj in cls.objects(graph):
            cls.xform_object(graph, obj)


class PartitionTransformer(GraphTransformer):
    """
    Transforms nodes that are partitions.

    Sets node label to device name rather than device path.
    Sets node shape to rectangle.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['label'] = os.path.basename(
           Utils.get_attr(obj, ['UDEV', 'DEVPATH'])
        )
        obj.attr['shape'] = "rectangle"

    @classmethod
    def objects(cls, graph):
        return (n for n in graph.iternodes() if \
           Utils.is_node_type(n, NodeTypes.DEVICE_PATH) and \
           Utils.get_attr(n, ['UDEV', 'DEVTYPE']) == 'partition')


class PartitionedDiskTransformer(GraphTransformer):
    """
    Transforms a partitioned disk into a partitioned node.

    Does not do anything if the disk has no partitions or if some
    non-partition edges point to any partitions.
    """

    @staticmethod
    def xform_object(graph, obj):
        partition_edges = [e for e in graph.out_edges(obj) if \
           Utils.is_edge_type(e, EdgeTypes.PARTITION)]

        # If there are no partitions in this disk, do nothing
        if not partition_edges:
            return

        # partitions to include in label
        partitions = [e[1] for e in partition_edges]

        # edges to partitions that are not partition edges from node
        keep_edges = [e for e in graph.in_edges(partitions) \
           if e not in partition_edges]

        # Due to a a bug in pygraphviz, can not fix up edges to partitions.
        # If additional edges exist, skip.
        # See: https://github.com/pygraphviz/pygraphviz/issues/76
        if keep_edges:
            return

        # No edges besides partition edges, so build HTML label
        node_row = "<tr><td colspan=\"%s\">%s</td></tr>" % \
           (len(partitions) + 1, Utils.get_attr(obj, ['UDEV', 'DEVPATH']))

        partition_names = sorted(
           os.path.basename(Utils.get_attr(p, ['UDEV', 'DEVPATH'])) for \
              p in partitions
        )
        partition_data = reduce(
           lambda x, y: x + y,
           ("<td port=\"%s\">%s</td>" % (n, n) for n in partition_names),
           ""
        )
        partition_row = "<tr>%s</tr>" % (partition_data + "<td> </td>")
        table = HTMLUtils.make_table([node_row, partition_row])
        HTMLUtils.set_html_label(obj, table)

        # delete partition nodes, since they are accounted for in label
        graph.delete_nodes_from(partitions)

    @classmethod
    def objects(cls, graph):
        return (n for n in graph.iternodes() if \
           Utils.is_node_type(n, NodeTypes.DEVICE_PATH) and \
           Utils.get_attr(n, ['UDEV', 'DEVTYPE']) == 'disk')


class SpindleTransformer(GraphTransformer):
    """
    Make every actual physical spindle an octagon.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['shape'] = "octagon"

    @classmethod
    def objects(cls, graph):
        return [n for n in graph.iternodes() if \
           Utils.is_node_type(n, NodeTypes.WWN)]


class PartitionEdgeTransformer(GraphTransformer):
    """
    Make partition edges dashed.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['style'] = 'dashed'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iteredges() if \
           Utils.is_edge_type(e, EdgeTypes.PARTITION))


class CongruenceEdgeTransformer(GraphTransformer):
    """
    Make congruence edges dotted.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['style'] = 'dotted'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iteredges() if \
           Utils.is_edge_type(e, EdgeTypes.CONGRUENCE))


class RemovedNodeTransformer(GraphTransformer):
    """
    Decorate removed nodes.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['style'] = 'dashed'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iternodes() if \
           Utils.is_diff_status(e, DiffStatuses.REMOVED))


class AddedNodeTransformer(GraphTransformer):
    """
    Decorate added nodes.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['style'] = 'filled'
        obj.attr['color'] = 'lightgray'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iternodes() if \
           Utils.is_diff_status(e, DiffStatuses.ADDED))


class AddedEdgeTransformer(GraphTransformer):
    """
    Decorate added edges.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['penwidth'] = '7.0'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iteredges() if \
           Utils.is_diff_status(e, DiffStatuses.ADDED))


class RemovedEdgeTransformer(GraphTransformer):
    """
    Decorate removed edges.
    """

    @staticmethod
    def xform_object(graph, obj):
        obj.attr['penwidth'] = '0.02'

    @classmethod
    def objects(cls, graph):
        return (e for e in graph.iteredges() if \
           Utils.is_diff_status(e, DiffStatuses.REMOVED))


class GraphTransformers(object):
    """
    A class that orders and does all graph transformations.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def xform(graph, klasses):
        """
        Transform a graph for more helpful viewing.

        :param `A_Graph` graph: the networkx graph
        :param klasses: a list of transformation classes
        :type klasses: list of `GraphTransformer`
        """
        for klass in klasses:
            klass.xform(graph)
