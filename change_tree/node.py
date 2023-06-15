from __future__ import annotations

from base_classes.node import BaseNode
from tree_sitter_wrapper.node import Node as TreeSitterNode

class Node(BaseNode):
    def __init__(
        self,
        id: str,
        child_rank: int,
        type: str,
        value: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
    ):
        super().__init__(type)
        self.id_ = id
        self.child_rank_ = child_rank
        self.value_ = value
        self.parent_ = parent
        if value:
            self.text = value.encode("utf-8")

        if not children:
            self.children_ = []
        else:
            self.children_ = children

    @property
    def id(self) -> str:
        """
        Generate an id for a node that's unique to the node.

        Parameter 'node' must have properties 'type', 'parent', and 'children'

        """

        return self.id_

    @property
    def parent(self) -> Node | None:
        return self.parent_

    @parent.setter
    def parent(self, new_parent: Node) -> None:
        self.parent_ = new_parent

    @property
    def children(self) -> list[Node]:
        return self.children_

    @property
    def value(self) -> str | None:
        return self.value_

    @property
    def child_rank(self) -> int:
        return self.child_rank_


def from_sitter_node(sitter_node: TreeSitterNode):
    """Construct ChangeTree node from TreeSitter node object."""
    return Node(
        sitter_node.id,
        sitter_node.child_rank,
        sitter_node.type,
        sitter_node.value,
    )
