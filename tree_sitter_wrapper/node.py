from __future__ import annotations
import hashlib

from tree_sitter import Node as RawNode

from base_classes.node import BaseNode


class Node(BaseNode):
    def __init__(self, raw_node_: RawNode):
        super().__init__(raw_node_.type)
        self.raw_node: RawNode = raw_node_

    @property
    def id(self) -> str:
        """
        Generate an id for a node that's unique to the node.

        Parameter 'node' must have properties 'type', 'parent', and 'children'

        """

        str_repr = f"{self.relative_id}_{self.to_node_path}"

        # have to hash cause of possible illegal characters
        return f"node_{hashlib.md5(str_repr.encode()).hexdigest()}"

    @property
    def parent(self) -> Node | None:
        if self.raw_node.parent:
            return Node(self.raw_node.parent)
        return None

    @property
    def children(self) -> list[Node]:
        return [Node(child) for child in self.raw_node.children]

    @property
    def value(self) -> str | None:
        return self.raw_node.text.decode(encoding="utf-8", errors="ignore")

    @property
    def child_rank(self) -> int:
        rank = 0
        if self.parent:
            for sibling in self.parent.children:
                if sibling.raw_node == self.raw_node:
                    break
                elif sibling.type == self.type:
                    rank += 1

        return rank

    def walk(self):
        return self.raw_node.walk()

    def get_unvisited_children(self, visited_nodes: list[RawNode]) -> list[tuple[int, Node]]:
        unvisited_children = []
        for idx, child in enumerate(self.children):
            if child.raw_node not in visited_nodes:
                unvisited_children.append((idx, child))

        return unvisited_children


def update_visited_nodes(node: Node, visited_nodes: list[RawNode]) -> None:
    """
    Updates a list of visited nodes by considering a node in params already visited. Each element in the list is a node
    who's all children is already visited

    Args:
        node: The node that is being checked if it is already visited
        visited_nodes: List of visited nodes in which all elements have all their children and themselves already visited

    Returns: None

    """
    if not node:
        return

    for child in node.children:
        if child.raw_node not in visited_nodes:
            return

    visited_nodes.append(node.raw_node)
    update_visited_nodes(node.parent, visited_nodes)
