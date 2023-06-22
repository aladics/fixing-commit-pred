from __future__ import annotations

from tree_sitter import Language, Parser
from itertools import chain
from typing import Iterator
import random
from pathlib import Path

from tree_sitter_wrapper.node import Node, update_visited_nodes
from common.commit_method import CommitMethodDefinition
from common.root_path import RootPath
from tree_sitter import Node as RawNode

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

    def get_random_leaf(self, visited_nodes: list[RawNode]) -> Node | None:
        """
        Get a random leaf in the tree by uniform randomly selecting a children at each node until a leaf is reached
        while not traversing any node that has been traversed before in visited_nodes

        Args:
            visited_nodes: List of visited nodes

        Returns:
            A leaf (terminal) node in the tree, or None if every node is already visited
        """
        node = self.root

        while not node.is_leaf():
            unvisited_children = node.get_unvisited_children(visited_nodes)
            if len(unvisited_children) == 0:
                return None
            node = random.choice(unvisited_children)[1]

        return node

    def get_random_root_paths(self, n_paths: int) -> list[RootPath]:
        """
        Get randomly generated root paths.

        Args:
            n_paths: The number of root paths to randomly get

        Returns:
            Set of root paths (no duplicates)
        """
        root_paths = []
        visited_nodes = []

        while len(root_paths) < n_paths:
            node = self.get_random_leaf(visited_nodes)
            if not node:
                break

            root_paths.append(self.get_root_path(node))
            update_visited_nodes(node, visited_nodes)

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
    """
    Extract the AST for a file

    Args:
        filepath: The file to extract AST for

    Returns:

    """
    filepath = Path(filepath)

    with filepath.open("rb") as fp:
        file_content = fp.read(-1)

    ast = parser.parse(file_content)
    return TreeSitterTree(Node(ast.root_node))


def get_sitter_AST_method(filepath: Path | str, commit_method: CommitMethodDefinition) -> TreeSitterTree:
    """
    Parses the TreeSitter AST for a method

    Args:
        filepath: Path to the file containing the method
        commit_method: The method to extract AST for

    Returns: TreeSitterTree object

    """
    return get_sitter_AST_file(filepath).get_method_by_pos(commit_method.line, commit_method.col)
