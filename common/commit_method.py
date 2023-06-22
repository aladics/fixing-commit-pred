from __future__ import annotations


class CommitMethodDefinition:
    """
    Represents a method definition in a commit.

    """

    def __init__(self, repo: str, sha: str, filepath: str, url: str, identifier: str, pos: str):
        self.repo = repo
        self.sha = sha
        self.filepath = filepath
        self.url = url
        self.identifier = identifier

        positions = pos.split(":")
        self.line = int(positions[0])
        self.col = int(positions[1])


def csv_line_parser_base(line: str, repo_idx: int, sha_idx: int, filepath_idx: int, url_idx: int, identifier_idx: int,
                         pos_idx: int) -> CommitMethodDefinition:
    """

    Args:
        line: A line from the dataset (csv)
        repo_idx: The column index of the repository
        sha_idx: The column index of the commit hash
        filepath_idx: The column index of the filepath
        url_idx: The column index of the URL
        pos_idx: The column index of the position

    Returns: Corresponding CommitMethodDefinition object

    """
    fields = line.split(",")
    return CommitMethodDefinition(repo=fields[repo_idx], sha=fields[sha_idx], filepath=fields[filepath_idx],
                                  url=fields[url_idx], identifier=fields[identifier_idx], pos=fields[pos_idx])
