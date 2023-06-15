from functools import partial

from common.commit_method import csv_line_parser_base
from common.config import CONFIG
from change_tree.tree import ChangeTree
from change_tree.tree import from_commit_methods as chtree_from_commit_methods
from change_tree.util import dump_gv
from common.util import get_lines_from_file

parse_pre_commit_method_def = partial(csv_line_parser_base, repo_idx=0, sha_idx=8, filepath_idx=3, pos_idx=5)
parse_post_commit_method_def = partial(csv_line_parser_base, repo_idx=0, sha_idx=9, filepath_idx=4, pos_idx=6)


def parse_csv_line(line: str) -> ChangeTree:
    """
    Parse a csv line to a Change Tree object

    Args:
        line: The line to parse

    Returns: The change tree based on csv line

    """
    pre_method = parse_pre_commit_method_def(line)
    post_method = parse_post_commit_method_def(line)

    return chtree_from_commit_methods(pre_method, post_method, CONFIG.summer23_dataset_files_root)


def parse_csv() -> None:
    """
    Parse the summer23 (commit fixes) dataset
    """
    csv_lines = get_lines_from_file(CONFIG.summer23_dataset_path)[1:]

    for line in csv_lines:
        ch_tree = parse_csv_line(line)
        ch_tree.create_before()
        dump_gv(ch_tree, "PATH_TO_GV")
