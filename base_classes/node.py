from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

import hashlib


@dataclass
class BaseNode(ABC):
    type: str

    @property
    @abstractmethod
    def parent(self) -> BaseNode | None:
        pass

    @property
    @abstractmethod
    def children(self) -> list[BaseNode]:
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def value(self) -> str | None:
        pass

    @property
    @abstractmethod
    def child_rank(self) -> int:
        pass

    @property
    def ancestors(self) -> list[BaseNode]:
        parents = []

        parent = self.parent
        while parent:
            parents.append(parent)
            parent = parent.parent

        return parents

    @property
    def to_node_path(self) -> str:
        concated_ids = ""

        for ancestor in self.ancestors:
            concated_ids += ancestor.relative_id

        return concated_ids

    @property
    def ast_identifier(self) -> str | None:
        """Get the node's identifier, if it has one"""
        if self.is_leaf():
            return self.value
        return None

    @property
    def relative_id(self) -> str:
        """
        Get id for node that is unique as part of a path.
        """
        str_repr = f"{len(self.ancestors)}_{self.child_rank}_{self.type}"

        ast_id = self.ast_identifier
        if ast_id:
            str_repr = f"{str_repr}_{ast_id}"

        # have to hash cause of possible illegal characters
        return f"node_{hashlib.md5(str_repr.encode()).hexdigest()}"

    @property
    def repr(self) -> str:
        """
        Get human readable, non-unique node representation.

        :param Node node: The node to represent.
        """

        node_repr: str = self.type
        if self.is_leaf() and self.value and self.type != self.value:
            node_repr += ": " + self.value

        return node_repr

    def is_repr_same(self, other: BaseNode) -> bool:
        return self.id == other.id

    def is_leaf(self) -> bool:
        return len(self.children) == 0
