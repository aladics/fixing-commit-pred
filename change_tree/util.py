from base_classes.node import BaseNode


def get_node_seq_repr(node_seq: list[BaseNode]) -> list[str | None]:
    """
    Get the node representation for each node in a sequence.

    Args:
        node_seq: Sequence of nodes to generate the representation for

    Returns: A sequence of strings corresponding to the node representations

    """

    return [node.repr for node in node_seq]
