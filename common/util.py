from pathlib import Path


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
