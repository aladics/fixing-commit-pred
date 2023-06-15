import base_classes.node


class RootPath:
    def __init__(self, path: list[base_classes.node.BaseNode]):
        self.path = path
        self.node_ids = [node.id for node in path]

    def __hash__(self):
        return hash((*self.node_ids,))

    def __eq__(self, other):
        if len(self.node_ids) != len(other.node_ids):
            return False

        for i in range(len(self.node_ids)):
            if self.node_ids[i] != other.node_ids[i]:
                return False

        return True

    def __repr__(self) -> str:
        path_repr = f"{self.path[0].repr} -> {self.path[1].repr} -> ... -> {self.path[-2].repr} -> {self.path[-1].repr}"

        return path_repr
    