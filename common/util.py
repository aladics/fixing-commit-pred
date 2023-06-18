from pathlib import Path
import subprocess

from base_classes.node import BaseNode
from change_tree.tree import ChangeTree
from tree_sitter_wrapper.tree import TreeSitterTree


def get_lines_from_file(path: str) -> list[str]:
    """
    Get the lines of a file

    Args:
        path: The path to the file whose lines we are getting

    Returns: List of lines (strings)

    """
    with Path(path).open() as fp:
        lines = fp.readlines()

    return lines


def get_gv_repr(tree: ChangeTree | TreeSitterTree) -> str:
    """
    Get the GraphViz repr for a given tree.

    Args:
        tree: The tree for which the GV repr should be fetched

    Returns: The gv representation as string

    """

    if not tree.get_root():
        return ""

    nodes: list[BaseNode] = [tree.get_root()]

    edges = []
    labels = []

    while nodes:
        node = nodes.pop()
        node_id = node.id

        if node.is_leaf():
            label = node.repr.replace('"', '\\"')
            labels.append(f'{node_id} [label="{label}"]')
            continue

        labels.append(f'{node_id} [label="{node.repr}"]')
        for child in node.children:
            edges.append(f"{node_id} -> {child.id};")
            nodes.append(child)

    lines = ["digraph G{"]
    lines += edges
    lines.append("")
    lines += labels
    lines.append("}")

    return "\n".join(lines)


def dump_gv(tree: TreeSitterTree | ChangeTree, filepath: str | Path) -> None:
    """
    Dumps a tree's gv representation to a file.

    Args:
        tree: The tree object for which we want to generate the gv representation
        filepath: The filepath to save the gv representation to

    Returns:
        None
    """
    filepath = Path(filepath)

    gv_repr = get_gv_repr(tree)
    with filepath.open("w") as f:
        f.write(gv_repr)


def dump_tree_to_png(tree: TreeSitterTree | ChangeTree, filepath: str | Path) -> None:
    """
    Dumps the tree to a png image. For this function to work the graphviz "dot" package must be installed on the system

    Args:
        tree: The tree object for which we want to generate the png
        filepath: The filepath to save the image to

    Returns:
        None
    """
    filepath = Path(filepath)
    gv_filepath = filepath.parent / f"{filepath.stem}.gv"

    dump_gv(tree, gv_filepath)
    try:
        with filepath.open("w") as fp:
            subprocess.run(['dot', '-Tpng', str(gv_filepath)], stdout=fp, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating the PNG: {e}")
        raise
    finally:
        gv_filepath.unlink()
