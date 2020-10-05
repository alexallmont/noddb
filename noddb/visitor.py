from __future__ import annotations


class VisitorException(Exception):
    """
    Exception thrown if a concrete node has not implemented a visit function.
    This will only occur for nodes that derive from NodeBase rather than Node.
    """
    pass


class Visitor:
    def on_node_enter(self, node: Node):
        """
        Callback when entering, or descending into, a node in hierarchy.
        :param node: node in hierarchy
        """
        pass

    def on_node_exit(self, node: Node):
        """
        Callback when existing, or popping out from, a node in hierarchy.
        :param node: node in hierarchy
        """
        pass

    def on_node_array_enter(self, node: NodeArray):
        """
        Callback when entering, or descending into, a node array.
        :param node: node in hierarchy
        """
        pass

    def on_node_array_exit(self, node: NodeArray):
        """
        Callback when existing, or popping out from, a node array.
        :param node: node in hierarchy
        """
        pass

    def on_input(self, value: InputValue):
        """
        Callback when an input value has been found in traversal
        :param value: value in hierarchy
        :return:
        """
        pass

    def on_output(self, value: OutputValue):
        """
        Callback when an input value has been found in traversal
        :param value: value in hierarchy
        :return:
        """
        pass
