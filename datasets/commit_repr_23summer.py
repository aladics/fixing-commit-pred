from functools import partial
from pathlib import Path
import pickle
import logging
from logging.handlers import RotatingFileHandler


import requests
from tqdm import tqdm

from common.commit_method import csv_line_parser_base, CommitMethodDefinition
from common.config import CONFIG
from common.util.figure import get_lines_from_file, dump_tree_to_png
from common.util.misc import download_file
from change_tree.tree import ChangeTree
from tree_sitter_wrapper.tree import get_sitter_AST_method

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s| %(levelname)s] %(message)s', datefmt="%y. %m. %d %H:%M")
file_handler = RotatingFileHandler(CONFIG.log_file, maxBytes=10000000, backupCount=2)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

parse_pre_commit_method_def = \
    partial(csv_line_parser_base, repo_idx=0, sha_idx=8, filepath_idx=3, url_idx=1, identifier_idx=7, pos_idx=5)
parse_post_commit_method_def = \
    partial(csv_line_parser_base, repo_idx=0, sha_idx=9, filepath_idx=4, url_idx=2, identifier_idx=7, pos_idx=6)


def get_dst_path(commit_method: CommitMethodDefinition) -> Path:
    """
    Get the path to the local file given by commit_method

    Args:
        commit_method: The commit method to get the local path to

    Returns: Path object corresponding to the method

    """
    repo_part = commit_method.repo.replace('/', '_')

    # Keep only last 20 of path to avoid huge paths
    filepath_part = str(Path(commit_method.filepath).parent).replace('\\', '_')[-20:]

    return Path(CONFIG.summer23_dataset_files_root) / f"{repo_part}_{commit_method.sha}" / filepath_part / \
        Path(commit_method.filepath).name


def chtree_from_commit_methods(pre_commit_method: CommitMethodDefinition,
                               post_commit_method: CommitMethodDefinition) -> ChangeTree:
    """
    Get a ChangeTree object for a commit method

    Args:
        pre_commit_method: a CommitMethod object for the pre commit state
        post_commit_method: a CommitMethod object for the post commit state

    Returns: ChangeTree object

    """
    pre_tree = get_sitter_AST_method(get_dst_path(pre_commit_method), pre_commit_method)
    post_tree = get_sitter_AST_method(get_dst_path(post_commit_method), post_commit_method)

    return ChangeTree(pre_tree, post_tree)


def download_commit_file(commit_method: CommitMethodDefinition) -> None:
    """
    Downloads the file corresponding to the commit method

    Args:
        commit_method: The commit method to get the containing file for

    Returns: None

    """
    dst_file_path = get_dst_path(commit_method)

    if dst_file_path.exists():
        return

    download_file(commit_method.url, dst_file_path)


def parse_csv_line(line: str) -> tuple[ChangeTree, CommitMethodDefinition, CommitMethodDefinition]:
    """
    Parse a csv line  after downloading the files needed for it (files corresponding to pre and
    post states)

    Args:
        line: The line to parse

    Returns: Tuple of: the change tree based on csv line, pre-commit method, post-commit method

    """
    pre_method = parse_pre_commit_method_def(line)
    post_method = parse_post_commit_method_def(line)

    download_commit_file(pre_method)
    download_commit_file(post_method)

    return chtree_from_commit_methods(pre_method, post_method), pre_method, post_method


def save_chtree(ch_tree: ChangeTree, commit_method: CommitMethodDefinition) -> Path:
    repo_part = commit_method.repo.replace("/", "_")
    filename_part = Path(commit_method.filepath).name.replace(".", "_")

    dst_path = Path(CONFIG.summer23_chtree_root) / f"{repo_part}_{commit_method.sha}" / filename_part / \
        f"{commit_method.identifier}.pkl"

    dst_path.parent.mkdir(exist_ok=True, parents=True)

    with dst_path.open("wb") as fp:
        pickle.dump(ch_tree, fp)


def parse_csv() -> None:
    """
    Parse the summer23 (commit fixes) dataset
    """
    logger.info(f"Start parsing CSV from dataset '{CONFIG.summer23_dataset_path}'")
    csv_lines = get_lines_from_file(CONFIG.summer23_dataset_path)[1:]

    n_fail = 0
    with tqdm(total=len(csv_lines), desc="Processing dataset") as pbar:
        for idx, line in tqdm(enumerate(csv_lines)):
            logger.info(f"Parsing and getting data for line idx '{idx}'")
            try:
                ch_tree, pre_method, post_method = parse_csv_line(line)
            except requests.exceptions.HTTPError as ex:
                logger.error("HTTP Error: ", ex)
                n_fail += 1
                continue
            except Exception as ex:
                logger.error("Error: ", ex)
                n_fail += 1
                continue
            finally:
                pbar.update(1)
                pbar.set_postfix({"Fails": n_fail})

            save_chtree(ch_tree, post_method)
            ch_tree.create_after()
            dump_tree_to_png(ch_tree, "F:/work/kutatas/datasets/tmp/hello.png")
            logger.info(f"Generated ChangeTree for repo '{post_method.repo}', commit '{post_method.sha}', "
                        f"file '{Path(post_method.filepath).name}', method '{post_method.identifier}")

    logger.info(f"Start parsing CSV from dataset '{CONFIG.summer23_dataset_path}'")
