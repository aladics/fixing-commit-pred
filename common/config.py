from pathlib import Path

from pydantic import BaseModel
import yaml

CONFIG_PATH = "config.yaml"


class Config(BaseModel):
    summer23_dataset_files_root: str
    summer23_dataset_path: str


def get_config():
    with Path(CONFIG_PATH).open() as fp:
        config_content = yaml.safe_load(fp)
    return Config(**config_content)


CONFIG = get_config()
