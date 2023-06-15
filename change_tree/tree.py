from dataclasses import dataclass, field
from typing import Iterator
from pathlib import Path

from tree_sitter_wrapper.tree import TreeSitterTree, get_sitter_AST_method

from common.root_path import RootPath
from common.commit_method import CommitMethodDefinition
from common import config
from change_tree import node
from tree_sitter_wrapper.node import Node as TreeSitterNode


@dataclass
class ChangeTree:
    before_tree: TreeSitterTree
    after_tree: TreeSitterTree
    max_root_paths: int = 200
    root: node.Node | None = field(init=False)

    def __post_init__(self):
        self.before_paths = [
            RootPath(path) for path in self.before_tree.get_root_paths(self.max_root_paths)
        ]
        self.after_paths = [
            RootPath(path) for path in self.after_tree.get_root_paths(self.max_root_paths)
        ]

        self.root = None

    def get_root(self) -> node.Node:
        """
        Get the ChangeTree root
        """
        return self.root

    def traverse(self) -> Iterator[node.Node]:
        """
        Do BFS on the tree.
        """

        visited_nodes = []
        current_node = self.root

        while current_node:
            if not any(current_node.id == visited_node.id for visited_node in visited_nodes):
                yield current_node
                visited_nodes.append(current_node)

            traverse_up = True
            for child in current_node.children:
                if not any(child.id == visited_node.id for visited_node in visited_nodes):
                    current_node = child
                    traverse_up = False
                    break

            if traverse_up:
                current_node = current_node.parent

    def create_path_diffs(
            self, base_set: list[RootPath], other_set: list[RootPath]
    ) -> None:
        """

        Args:
            base_set: The set whose unique paths we are interested in
            other_set:  The set whose paths we are removing
        """
        self.root = None

        changed_paths = set()
        changed_paths.update(base_set)
        changed_paths.difference_update(other_set)
        changed_paths = sorted(changed_paths, key=lambda el: base_set.index(el))

        for changed_path in changed_paths:
            self.add_root_path(changed_path.path)

    def create_before(self) -> None:
        """
        Creates the change tree relative to the before state of the code change.
        """
        self.create_path_diffs(self.before_paths, self.after_paths)

    def create_after(self) -> None:
        """
        Creates the change tree relative to the after state of the code change.
        """
        self.create_path_diffs(self.after_paths, self.before_paths)

    def add_root_path(self, root_path: list[TreeSitterNode]) -> None:
        """
        Add a root path to construct the change tree.

        Args:
            root_path: List of TreeSitter nodes to be added to the change tree
        """

        root_in_path: node.Node = node.from_sitter_node(
            root_path[0]
        )

        if self.root is None:
            self.root = root_in_path
        elif not self.root.is_repr_same(root_in_path):
            raise ValueError(
                "Root is inconsistent: it must be the same for all root-paths"
            )

        parent = self.root
        for node_in_path in root_path[1:]:

            next_node = None
            for node_in_tree in parent.children:
                if node_in_tree.is_repr_same(node_in_path):
                    next_node = node_in_tree
                    break

            if next_node:
                parent = next_node
            else:
                new_node = node.from_sitter_node(node_in_path)

                new_node.parent = parent
                parent.children.append(new_node)
                parent = new_node


def from_commit_methods(pre_commit_method: CommitMethodDefinition,
                        post_commit_method: CommitMethodDefinition, files_root: Path | str) -> ChangeTree:
    files_root = Path(files_root)

    pre_tree = get_sitter_AST_method(files_root / 'pre', pre_commit_method)
    post_tree = get_sitter_AST_method(files_root / 'post', post_commit_method)

    return ChangeTree(pre_tree, post_tree)
