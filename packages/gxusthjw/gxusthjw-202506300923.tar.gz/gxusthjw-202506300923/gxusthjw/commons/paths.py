#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        paths.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“路径”相关的工具。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/15     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from pathlib import Path

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define tools associated with 'path'.
"""

__all__ = [
    'UniquePathGenerationError',
    'gen_unique_path'
]


# 定义 ==============================================================

class UniquePathGenerationError(Exception):
    """
    当无法生成唯一路径时抛出的异常
    """
    pass


def gen_unique_path(
        parent_path: str | Path,
        file_base_name: str, file_ext_name: str = '',
        max_attempts: int = 1000,
        create: bool = False
) -> str:
    """
    在指定的父目录下生成唯一的文件或目录的路径。

        注意：当file_ext_name为空时，生成的路径为目录路径，
             否则生成的路径为文件的路径。

    :param parent_path: 父目录的路径，可以是字符串或 Path 对象。
    :param file_base_name: 文件的基本名称，不包括扩展名。
    :param file_ext_name: 文件的扩展名，默认为空。
    :param max_attempts: 尝试生成唯一文件名的最大次数，默认为1000。
    :param create: 是否创建文件或目录，默认为False。如果为True，将创建文件或目录。
    :return: 生成的唯一文件或目录的路径。
    """

    # 参数校验
    if not isinstance(file_base_name, str):
        raise TypeError("file_base_name must be a string")
    file_base_name = file_base_name.strip()
    if not file_base_name:
        raise ValueError("file_base_name cannot be empty")

    if not isinstance(file_ext_name, str):
        raise TypeError("file_ext_name must be a string")
    file_ext_name = file_ext_name.strip()
    if file_ext_name and not file_ext_name.startswith('.'):
        file_ext_name = '.' + file_ext_name

    if not isinstance(max_attempts, int) or max_attempts <= 0:
        raise ValueError("max_attempts must be a positive integer")

    # 统一处理路径
    parent_path = Path(parent_path).resolve()

    # 确保父路径存在
    if create:
        parent_path.mkdir(parents=True, exist_ok=True)

    for counter in range(max_attempts):
        if counter == 0:
            filename = f"{file_base_name}{file_ext_name}"
        else:
            filename = f"{file_base_name}_copy{counter}{file_ext_name}"

        full_path = (parent_path / filename).resolve()

        if not full_path.exists():
            if file_ext_name == '':
                if create:
                    full_path.mkdir(exist_ok=True)
            else:
                if create:
                    full_path.touch(exist_ok=True)
            return str(full_path)

    raise UniquePathGenerationError(
        f"Unable to generate a unique path under the parent path '{parent_path}', "
        f"maximum attempt count {max_attempts} has been reached."
    )
