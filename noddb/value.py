from __future__ import annotations
from .node import Node, NodeContainer


class ValueException(Exception):
    """
    This exception is raised if there is a problem setting what is stored in the
    value, or for invalid connections between outputs and inputs.
    """
    pass


class ValueBase(Node):
    """
    Abstract base for storing a value in a node. This is a child of a node so
    derives from Node to inherit the parent-child behaviour. Concrete values
    are either inputs or outputs, which have different behaviour for setting
    values and for connectability.
    """
    def __init__(self, node: NodeContainer, name: str, value):
        super().__init__(parent=node, name=name)
        self._value = value

    def is_input(self):
        return False

    def is_output(self):
        return False

    def value(self):
        return self._value

    def set_value(self, value):
        if type(self._value) != type(value):
            raise ValueException(
                'Cannot set "{}" ({}) to mismatched value {} ({})'.format(
                    self.path(),
                    type(self._value).__name__,
                    value,
                    type(value).__name__
                )
            )
        self._value = value


class OutputValue(ValueBase):
    """
    An output is a value that has a right shift >> operator so it may be
    connected to any number of inputs, overriding their value.
    """
    def is_output(self):
        return True

    def __rshift__(self, input_value: InputValue):
        input_value.set_source(self)


class InputValue(ValueBase):
    """
    An input is a value that may be overridden by being connected to a
    specific output. This 'sourcing' of the the input value allows data
    to flow through the node-value graph.
    """
    def __init__(self, node: NodeBase, name: str, value):
        super().__init__(node, name, value)
        self._source = None

    def is_input(self):
        return True

    def value(self):
        if self._source:
            self._value = self._source.value()
        return self._value

    def set_value(self, value):
        if self._source:
            raise ValueException(
                'Cannot set "{}" whilst sourced from "{}"'.format(
                    self.path(),
                    self._source.path()
                )
            )
        super().set_value(value)

    def is_sourced(self):
        return self._source is not None

    def source(self):
        if self._source:
            return self._source
        return None

    def set_source(self, output: OutputValue):
        if not output.is_output():
            raise ValueException(f'Cannot source from non-output "{output.path()}"')

        if self._source:
            raise ValueException(
                'Cannot source "{}" from "{}" as already connected to "{}"'.format(
                    self.path(),
                    output.path(),
                    self._source.path()
                )
            )

        if not isinstance(self._value, type(output._value)):
            raise ValueException(
                'Cannot source "{}" ({}) to mismatched output "{}" ({})'.format(
                    self.path(),
                    type(self._value).__name__,
                    output.path(),
                    type(output._value).__name__
                )
            )
        self._source = output

    def clear_source(self):
        if not self._source:
            raise ValueException(f'Cannot clear source on non-connected input "{self.path()}"')
        self._source = None

    def __lshift__(self, output_value: OutputValue):
        self.set_source(output_value)
