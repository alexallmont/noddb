from .node import Node


class ValueException(Exception):
    pass


class Value(Node):
    def __init__(self, name, node, value, is_input):
        super().__init__(name, node)
        self._value = value
        self._input_source = None
        self._is_input = is_input

    def value(self):
        if self._input_source:
            self._value = self._input_source.value()
        return self._value

    def set_value(self, value):
        if self._input_source:
            raise ValueException(
                'Cannot set "{}" whilst sourced from "{}"'.format(
                    self.path(),
                    self._input_source.path()
                )
            )
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

    def is_input(self):
        return self._is_input

    def is_output(self):
        return not self._is_input

    def is_sourced(self):
        return self._input_source != None

    def source(self):
        if self._input_source:
            return self._input_source
        return None

    def set_source(self, output):
        if not self.is_input():
            raise ValueException(f'Cannot source to non-input "{self.path()}"')

        if not output.is_output():
            raise ValueException(f'Cannot source from non-output "{output.path()}"')

        if self._input_source:
            raise ValueException(
                'Cannot source "{}" from "{}" as already connected to "{}"'.format(
                    self.path(),
                    output.path(),
                    self._input_source.path()
                )
            )

        if type(self._value) != type(output._value):
            raise ValueException(
                'Cannot source "{}" ({}) to mismatched output "{}" ({})'.format(
                    self.path(),
                    type(self._value).__name__,
                    output.path(),
                    type(output._value).__name__
                )
            )
        self._input_source = output

    def clear_source(self):
        if not self._input_source:
            raise ValueException(f'Cannot clear source on non-connected input "{self.path()}"')
        self._input_source = None


class InputValue(Value):
    def __init__(self, name, node, value):
        super().__init__(name, node, value, True)


class OutputValue(Value):
    def __init__(self, name, node, value):
        super().__init__(name, node, value, False)
