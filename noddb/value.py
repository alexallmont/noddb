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
            raise ValueException(f'Cannot set input "{self.path()}" as value is already sourced from "{self._input_source.path()}"')
        if type(self._value) != type(value):
            raise ValueException(f'Cannot set input "{self.path()}" ({type(self._value).__name__}) to mismatched value of "{value}" ({type(value).__name__})')
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

    def set_source(self, output_value):
        if not output_value.is_output():
            raise ValueException(f'Cannot set non-output "{output_value.path()}" to a source')
        if self._input_source:
            raise ValueException(f'Cannot set already-connected input "{self.path()}" from output "{output_value.path()}"')
        if not self.is_input():
            raise ValueException(f'Cannot set non-input "{self.path()}" from a source')
        if type(self._value) != type(output_value._value):
            raise ValueException(f'Cannot set input "{self.path()}" ({type(self._value).__name__}) to mismatched output "{output_value.path()}" ({type(output_value._value).__name__})')
        self._input_source = output_value

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
