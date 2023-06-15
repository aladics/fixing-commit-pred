from dataclasses import dataclass


@dataclass
class Config:
    summer23_dataset_files_root: str
    summer23_dataset_path: str


def get_config():
    # TODO:
    return Config("TODO")


CONFIG = get_config()
