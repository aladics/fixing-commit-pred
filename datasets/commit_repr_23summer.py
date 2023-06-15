from functools import partial

from common.commit_method import csv_line_parser_base
from common.config import CONFIG
import change_tree
from common.util import get_lines_from_file

parse_pre_commit_method_def = partial(csv_line_parser_base, repo_idx=0, sha_idx=8, filepath_idx=3, pos_idx=5)
parse_post_commit_method_def = partial(csv_line_parser_base, repo_idx=0, sha_idx=9, filepath_idx=4, pos_idx=6)


def parse_csv_line(line: str) -> change_tree.tree.ChangeTree:
    """
    Parse a csv line to a Change Tree object

    Args:
        line: The line to parse

    Returns: The change tree based on csv line

    """
    pre_method = parse_pre_commit_method_def(line)
    post_method = parse_post_commit_method_def(line)

    return change_tree.tree.from_commit_methods(pre_method, post_method, CONFIG.summer23_dataset_files_root)


def parse_csv():
    """
    Parse the summer23 (commit fixes) dataset
    """
    csv_lines = get_lines_from_file(CONFIG.summer23_dataset_path)
    for line in csv_lines:
        ch_tree = parse_csv_line(line)
        change_tree.util.dump_gv(ch_tree, "TODO")



