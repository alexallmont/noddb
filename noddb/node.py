class NodeException(Exception):
    pass


class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        if parent:
            if name in parent.children:
                raise NodeException(f'parent "{parent.path()}" already has child "{name}"')
            parent.children[name] = self
        self.children = {}

    def is_input(self):
        return False

    def is_output(self):
        return False

    def path(self):
        if self.parent:
            return f'{self.parent.path()}.{self.name}'
        return self.name

    def __getitem__(self, child_name):
        if child_name not in self.children:
            raise NodeException(f'Node "{self.path()}" has no child "{child_name}"')
        return self.children[child_name]
