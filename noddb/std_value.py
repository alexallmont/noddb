from .node import NodeBase
from .value import InputValue, OutputValue


class OutputInt(OutputValue):
    def __init__(self, node: NodeBase, name: str, value: int = 0):
        super().__init__(node, name, int(value))


class OutputFloat(OutputValue):
    def __init__(self, node: NodeBase, name: str, value: float = 0.0):
        super().__init__(node, name, float(value))


class OutputString(OutputValue):
    def __init__(self, node: NodeBase, name: str, value: str = ''):
        super().__init__(node, name, str(value))


class OutputBool(OutputValue):
    def __init__(self, node: NodeBase, name: str, value: bool = False):
        super().__init__(node, name, bool(value))


class InputInt(InputValue):
    def __init__(self, node: NodeBase, name: str, value: int = 0):
        super().__init__(node, name, int(value))


class InputFloat(InputValue):
    def __init__(self, node: NodeBase, name: str, value: float = 0.0):
        super().__init__(node, name, float(value))


class InputString(InputValue):
    def __init__(self, node: NodeBase, name: str, value: str = ''):
        super().__init__(node, name, str(value))


class InputBool(InputValue):
    def __init__(self, node: NodeBase, name: str, value: bool = False):
        super().__init__(node, name, bool(value))


def standard_value_types():
    return [
        OutputInt,
        OutputFloat,
        OutputString,
        OutputBool,
        InputInt,
        InputFloat,
        InputString,
        InputBool
    ]
