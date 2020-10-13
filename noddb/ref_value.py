"""
Node references allow values to point to other nodes in the graph.
Note that this does not yet support type checking so should be used with caution.
Giving a node an OutputRef child indicates that one would like to reference that node
through a value elsewhere in the graph. An InputRef can be assigned to point to any
OutputRef and the path of that reference is stored during serialisation.
See test_ref_value for a concrete example.
"""

from .node import NodeBase
from .value import InputValue, OutputValue


class OutputRef(OutputValue):
    """
    A value which, when added to a node, allows that node to be referenced elsewhere
    from an InputRef.
    """
    def __init__(self, node: NodeBase, name: str):
        # Reuse the owning node as the value.
        super().__init__(node, name, node)

    def is_serialised(self):
        # Don't save this value. It's not necessary as the parent node's existence
        # makes this value's presence implicit.
        return False


class InputRef(InputValue):
    """
    An reference to a node elsewhere in the network. value() is overridden to return
    the node instance.
    """
    def __init__(self, node: NodeBase, name: str):
        super().__init__(node, name, None)

    def can_source_from(self, output: OutputValue):
        # Override sourcing rules to allow any output refs to be connected
        return isinstance(output, OutputRef)

    def value(self):
        # Get the OutputRef's value, which is the owning node
        ref = super().value()
        if not ref:
            return None
        return ref
