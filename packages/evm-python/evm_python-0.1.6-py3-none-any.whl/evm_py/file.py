def read_file(file_path: str, split: str = '\n'):
    try:
        contents = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip(split)
                if line == '':
                    continue
                contents.append(line)
        return contents
    except Exception as e:
        print(e)
        return None


import os
from pathlib import Path


def get_data_path(file_name: str):
    home_directory = os.environ.get("HOME")
    return Path(home_directory).joinpath('data', file_name)


def get_file_data(file_name: str, split: str = '\n'):
    return read_file(file_path=get_data_path(file_name=file_name), split=split)


import json


def get_json(file_path: str):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_data


def get_json_data(file_name: str):
    return get_json(file_path=get_data_path(file_name=file_name))
