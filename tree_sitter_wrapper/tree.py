from __future__ import annotations

from tree_sitter import Language, Parser
from itertools import chain
from typing import Iterator
import random
from pathlib import Path

from tree_sitter_wrapper.node import Node
from common.commit_method import CommitMethodDefinition
from common.root_path import RootPath

Language.build_library(
    # Store the library in the `build` directory
    "tree_sitter_wrapper/build/my-languages.so",
    # Include one or more languages
    ["tree_sitter_wrapper/vendor/tree-sitter-java"],
)

JAVA_LANGUAGE = Language("tree_sitter_wrapper/build/my-languages.so", "java")
parser = Parser()
parser.set_language(JAVA_LANGUAGE)


class TreeSitterTree:
    def __init__(self, root_node: Node):
        """
        Construct tree from its root node.
        """
        self.root = root_node

    def traverse(self) -> Iterator[Node]:
        """
        Do BFS on the tree.
        """
        cursor = self.root.walk()

        reached_root = False
        while not reached_root:
            yield Node(cursor.node)

            if cursor.goto_first_child():
                continue

            if cursor.goto_next_sibling():
                continue

            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True

                if cursor.goto_next_sibling():
                    retracing = False

    def get_root(self) -> Node:
        """
        Get the tree's root node.
        """
        return self.root

    def get_root_path(self, node: Node) -> RootPath:
        """
        Get the root path to the parameter node.
        """
        root_path = []

        while True:
            root_path = [node] + root_path
            if node == self.root:
                break

            node = node.parent

        return RootPath(root_path)

    def get_random_leaf(self) -> Node:
        """
        Get a random leaf in the tree by uniform randomly selecting a children at each node until we arrive at a leaf

        Returns:
            A leaf (terminal) node in the tree
        """
        node = self.root

        while not node.is_leaf():
            selected_child_idx = random.randint(0, len(node.children)-1)
            node = node.children[selected_child_idx]

        return node

    def get_random_root_paths(self, n_paths: int, max_tries=500) -> list[RootPath]:
        """
        Get randomly generated root paths.

        Args:
            n_paths: The number of root paths to randomly get
            max_tries: The max tries to get a new root path that is not already included

        Returns:
            Set of root paths (no duplicates)
        """
        root_paths = []

        n_tries = 0
        while n_tries < max_tries and len(root_paths) < n_paths:
            node = self.get_random_leaf()
            root_path = self.get_root_path(node)
            if root_path in root_paths:
                n_tries += 1
            else:
                root_paths.append(root_path)
                n_tries = 0

        return root_paths

    def get_root_paths(self, n_max_root_paths: int) -> list[RootPath]:
        """Get a number of root paths for the leaf nodes in the tree while traversing the tree in a BFS manner

        Args:
            n_max_root_paths: Maximum number of root_paths to get
        """
        root_paths = []

        for node in self.traverse():
            if len(root_paths) >= n_max_root_paths:
                break

            if node.is_leaf():
                root_paths.append(self.get_root_path(node))

        return root_paths

    def get_subtrees(self, node_type: str) -> Iterator[TreeSitterTree]:
        """Get every subtree for a specific type."""

        for node in self.traverse():
            if node.type == node_type:
                yield TreeSitterTree(node)

    def get_method_by_pos(self, line: int, col: int) -> TreeSitterTree | None:

        for method in chain(
                self.get_subtrees(node_type="method_declaration"),
                self.get_subtrees(node_type="constructor_declaration"),
        ):
            method_root = method.root.raw_node
            if method_root.start_point[0] <= line <= method_root.end_point[0]:
                return TreeSitterTree(method.root)


def get_sitter_AST_file(filepath: Path | str) -> TreeSitterTree:
    filepath = Path(filepath)

    with filepath.open("rb") as fp:
        file_content = fp.read(-1)

    ast = parser.parse(file_content)
    return TreeSitterTree(Node(ast.root_node))


def get_sitter_AST_method(files_root: Path | str, commit_method: CommitMethodDefinition) -> TreeSitterTree:
    return get_sitter_AST_file(files_root / commit_method.filepath).\
           get_method_by_pos(commit_method.line, commit_method.col)
