from __future__ import annotations

from tree_sitter_wrapper.node import Node as TreeSitterNode
from change_tree.node import from_sitter_node


class RootPath:
    def __init__(self, path: list[TreeSitterNode]):
        self.path = [from_sitter_node(node_) for node_ in path]
        self.node_ids = [node.id for node in path]
        self.cached_repr = ''.join(node.relative_id for node in path)
        self.cached_str_repr = f"{path[0].repr} -> {path[1].repr} -> ... -> " \
                               f"{path[-2].repr} -> {path[-1].repr}"

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
        return self.cached_repr

    def __lt__(self, value: RootPath) -> bool:
        return self.__repr__() < value.__repr__()

    def __str__(self) -> str:
        return self.cached_str_repr

    