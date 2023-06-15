import change_tree
from common.commit_method import CommitMethodDefinition


def test_chtree(before_commit_method: CommitMethodDefinition, after_commit_method: CommitMethodDefinition, files_root: str):
    ch_tree = change_tree.tree.from_commit_methods(before_commit_method, after_commit_method, files_root)
    change_tree.util.dump_gv(ch_tree, "asd.gv")


if __name__ == '__main__':
    test_chtree('PyCharm')

