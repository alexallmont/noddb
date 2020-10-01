from .node import Node


class ValueException(Exception):
    pass


class Value(Node):
    def __init__(self, name, node, value):
        super().__init__(name, node)
        self._value = value

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


class OutputValue(Value):
    def is_output(self):
        return True

    def __rshift__(self, input_value):
        input_value.set_source(self)


class InputValue(Value):
    def __init__(self, name, node, value):
        super().__init__(name, node, value)
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

    def set_source(self, output):
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

    def __lshift__(self, output_value):
        self.set_source(output_value)
