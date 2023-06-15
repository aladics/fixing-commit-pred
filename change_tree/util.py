from tree_sitter_wrapper.tree import TreeSitterTree
from change_tree.tree import ChangeTree
from base_classes.node import BaseNode

from pathlib import Path


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
    """
    filepath = Path(filepath)

    gv_repr = get_gv_repr(tree)
    with filepath.open("w") as f:
        f.write(gv_repr)


def get_node_seq_repr(node_seq: list[BaseNode]) -> list[str | None]:
    """
    Get the node representation for each node in a sequence.

    Args:
        node_seq: Sequence of nodes to generate the representation for

    Returns: A sequence of strings corresponding to the node representations

    """

    return [node.repr for node in node_seq]
