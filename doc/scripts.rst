Top-level Scripts
=================

Due to the existence of the top-level _graphs module, interacting with pydevDAG
by means of the Python interpreter is straightforward. However, pydevDAG also
provides a few small scripts for command-line interaction.

catdev
------
This script logs an entry into the journal which includes the
entire graph as the value of a field in the log entry.

cmpdev
------
This script compares two graphs.

diffdev
-------
This script generates a graph representing the difference of two graphs.

journaldev
----------
This script searches the journal for log entries containing a graph
and finds the difference between the two graphs nearest a given time stamp.

lsdev
-----
This script makes a graph of the existing storage configuration.
The default output is text, but it can also write the graph to a file.

showdev
-------
This script takes a previously stored graph and displays it in various formats.
