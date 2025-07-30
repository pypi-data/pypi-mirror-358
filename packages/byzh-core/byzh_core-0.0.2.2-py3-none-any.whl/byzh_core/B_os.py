import shutil
import os
from pathlib import Path
from typing import Literal

def get_parent_dir(path: Literal['__file__']) -> Path:
    '''
    获取 该py文件 所在的文件夹
    :param path: __file__
    '''
    parent_dir = Path(path).parent
    return parent_dir

def get_cwd() -> Path:
    '''
    获取 当前工作目录current working directory
    '''
    return Path.cwd()


def makedirs(path):
    def is_dir(path):
        path = Path(path)

        # 存在
        if os.path.isdir(path):
            return True

        # 不存在
        name = path.name
        if '.' in name:
            return False
        return True

    def is_file(path):
        path = Path(path)

        # 存在
        if os.path.isfile(path):
            return True

        # 不存在
        name = path.name
        if '.' in name:
            return True
        return False

    path = Path(path)

    if is_dir(path):
        os.makedirs(path, exist_ok=True)
    if is_file(path):
        os.makedirs(path.parent, exist_ok=True)

def rm(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    if os.path.isfile(path):
        os.remove(path)