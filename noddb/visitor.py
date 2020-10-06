# flake8: noqa - ignore circular imports when linting visit methods


class VisitorException(Exception):
    """
    Exception thrown if a concrete node has not implemented a visit function.
    This will only occur for nodes that derive from NodeBase rather than Node.
    """
    pass


class Visitor:
    def on_node_enter(self, node):
        """
        Callback when entering, or descending into, a node in hierarchy.
        :param node: node in hierarchy
        """
        pass

    def on_node_exit(self, node):
        """
        Callback when existing, or popping out from, a node in hierarchy.
        :param node: node in hierarchy
        """
        pass

    def on_node_array_enter(self, node):
        """
        Callback when entering, or descending into, a node array.
        :param node: node in hierarchy
        """
        pass

    def on_node_array_exit(self, node):
        """
        Callback when existing, or popping out from, a node array.
        :param node: node in hierarchy
        """
        pass

    def on_input(self, value):
        """
        Callback when an input value has been found in traversal
        :param value: value in hierarchy
        :return:
        """
        pass

    def on_output(self, value):
        """
        Callback when an input value has been found in traversal
        :param value: value in hierarchy
        :return:
        """
        pass
