NodDB
=====

NodDB - or noddy DB - is a simple graph database written in python. The intended audience is small projects which are still shaping their data requirements.

It provides:
 - A hierarchical node/value graph.
 - The ability to source data to input values from outputs of same type.
 - Registrar for marshalling to and from JSON and other persistent formats.
 - A concise definition system.

Motivation
----------

Many of the editors I've worked on have all had a solid data graph behind them where values can pass from one node to another. Usually this is a DAG, but some use cases were cyclic. To make these systems perform well requires significant investment.

NodDB is 'noddy' (meaning simpleton, numpty) by design because it throws that significant - and usually very important - time investment out of the window. It is a light structure to hang data on for experimental projects until they get to the point where the data requirements are absolutely clear. In short, it's a playpen data set.

The graph is loosely defined. It does not impose rules on cycles, topology, or inputs sourcing values from hierarchically distant nodes. It also does not have any caching or dirty-flagging system. It's simply provides a way of having values propagate through a graph and provides means to persist them.

NodDB may grow into a broader and robust system, but it's starting as the minimum I need to experiment with a few musical projects.

Node
----

A node has:
 - A name.
 - A parent (which may be None).
 - and a dictionary of children.

The children may be nodes or other values. Application-specific data can be bolted onto a node.

Value
-----

The bulk of the noddy shortcuts in NodDB is in the Value class. Values take design shortcut of being a derived from Node. This is not a clean OOP decision as a value isn't usually regarded as a node, and a proper graph would declare ports for connections. However, deriving from Node makes marshalling and internal management of the children simpler. As a Node, a Value has a name, parent node. A value may also be input or an output, and the connectivity of NodDB is implemented by allowing inputs to source their data from an output.

Value typing is strict. Rather than having a type defined explicitly, Values just store a default value and that type is checked for mismatches when changing it or sourcing it.

An input value may be 'sourced' from an output of another type. In a strict graph system this would be an edge connecting one vertex to another, which may have it's own properties. NodDB keeps it light and just stores a reference to the output in use. Once an input is connected it can't be modified; the output will provide it's value.

NodDB does not do any topological searching to check that values are propagated through the graph in order. If you are using a DAG, then you can brute force this by getting the nodes with no outputs and doing a breadth-first search back along the inputs.

Application Specifics
---------------------

Nodes and values do not have a strong definition, but the registrar can be used to define a factory used in serialisation. It assumes that these factory classes add any required child nodes and values.

Nodes (and hence values) have an `args` dictionary which may be used for application-specific arguments.
