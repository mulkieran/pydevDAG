Architecture
============

pydevDAG is configurable and flexible. At this point, it has no configuration
file or options. It is necessary to take advantage of its configurability
by editing its top-level file, _graphs.py. Each class
in _graphs.py represents a separate, configurable aspect of the graphing
operations.

Graph Generation and Decoration
-------------------------------
Graph generation makes use of the _structure module. This module defines
a number of classes which handle the addition of different types of nodes
or different categories of relationships to the graph. The contents of
the graph are determined by the choice of which of these classes participate
in building the graph.

Graph decoration is the process of adding additional information to nodes
or edges of the graph as desired. At present, all information is obtained
either from udev properties or sysfs attributes. The classes that manage
the decoration process and also obtaining suitable decorations are defined
in the _decorations module.

Writing the Graph to a File
---------------------------
It is necessary to convert some values in the graph to text in order to write
them in various graphical output formats. The _write module handles these
tasks as well as the inverse task of reading a file and converting text to
an object suitable for the graph.

Graphical Representation of the Graph
-------------------------------------
Display of the graph is currently handled by means of the graphviz library.
The graph is first converted to a an internal graphviz graph and is then
annotated with various graphviz attributes to enrich the visual display
with the most relevant information in the graph. This enrichment is
handled by the _display module. Each of the classes in the _display module
implements a different enrichment, and the choice of modules determines
the appearance of the graph.

Textual Representation of the Graph
-----------------------------------
Textual representation of the graph, in the form of a table is
also useful. The _print module handles the high-level organization of the
output, while the _print_helpers module consists of small classes that
handle the choice of values for individual columns.

Graph Comparison
----------------
It is helpful to determine programatically if there is a difference between one
graph and another. What makes two graphs equivalent is itself a configurable
notion. The _compare module allows defining multiple different notions of
equivalence. If two graphs are different, then the difference between them
can be calculated in various ways; the result is itself a graph.
