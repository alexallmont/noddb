# NodDB

NodDB is a very noddy graph database. The intended audience is small projects which are still figuring out their data requirements. It provides:
 - A hierarchical node/value graph.
 - Ability to source/connect input values from outputs of same type.
 - Registrar for marshalling to and from JSON and other persistent formats.
 - Very loose consise definition system.

# Motivation

This kind of connected DB is something I've had to reimplement many times on many projects. They're usually very tough systems that require a lot of boilerplate and design iteration. NodDB is a light structure to hang a design on whilst it's taking shape.

NodDB's graph is loosely defined. It does not impose rules on cycles or inputs sourcing values from hierarchicaly distant nodes, it's just a way of having values propagate through a graph and being able to persist the graph.

## Node

A node has a name, a parent (which may be None), and a list of children. The children may be nodes or other values. Other application-specific data can be tagged onto a node in `args`.

## Value

The bulk of the noddyness of NodDB is in the value. Values take an OOP shortcut of being a derived from Node. This makes marshalling and internal management of the children simpler. A value has a name, parent node, and may either be an input or an output.

An input value may be 'sourced' from an output of another type. In a strict graph system this would be an edge with properties, but NodDB keeps it light and just stores a reference to the output in use. Once an input is connected it can't be modified; the output will provide it's value.

Rather than having an expected type definied in a value definition, Values just store a default value and that type is checked for mismatches when changing it or sourcing it.

NodDB does not do any topological searching to check that values are propagated through the graph in order. If you are using a DAG, then you can brute force this by getting the nodes with no outputs and doing a breadth-first search back along the inputs.

## Application specifics

Nodes and values do not have a strong definition, but the registrar can be used to define a factory used in serialisation. It assumes that these factory classes add any required child nodes and values.

Nodes and values have an `args` dictionary which may be used for application-specific arguments.
