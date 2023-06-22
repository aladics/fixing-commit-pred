# Fixing commit comparator

This repo provides base for various commit representation but mainly the Change Tree based ones. 

## Prerequisites
- Python 10
- Pipenv
- C compiler (C/C++ Build tools for Windows) for TreeSitter

## Setting up
1. Copy config_default.yaml to config.yaml and set it's values accordingly
2. Create and sync virtual python environment with pipenv
```commandline
pipenv sync
```

## Usage
Most of the relevant scripts can be run as `pipenv run datasets.<dataset_id>`, or just `python datasets.<dataset_id>`
if already in pipenv shell
