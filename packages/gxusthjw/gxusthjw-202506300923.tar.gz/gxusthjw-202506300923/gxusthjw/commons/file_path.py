#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        file_path.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“文件路径”相关的函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import os
from typing import Tuple, Optional, List

# 声明 =============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the functions and classes associated with `file paths`.
"""

__all__ = [
    "sep_file_path",
    "join_file_path",
    "list_files_and_folders",
    "print_files_and_folders",
    "list_files_with_suffix",
    "get_root_path",
    "get_project_path",
    "get_this_path",
]


# 定义 ================================================================
def sep_file_path(file: str, with_dot_in_ext: bool = True) -> Tuple[str, str, str]:
    """
    将指定的文件完整路径分割为文件所在目录的路径，文件基名和文件扩展名。

    :param file: 文件的完整路径。
    :param with_dot_in_ext: 指定返回的文件扩展名中是否包含“.”，
                            如果为True，则包含，否则不包含。
    :return: (文件所在目录的路径, 文件基名，文件扩展名)
    """
    if not file:
        return "", "", ""
    file_path, file_name = os.path.split(file)
    if not file_name:
        return file_path, "", ""
    if file_name.startswith(".") and len(file_name) > 1:
        file_base_name = ""
        file_ext_name = file_name
    else:
        file_base_name, file_ext_name = os.path.splitext(file_name)
    if not file_ext_name:
        file_ext_name = ""
    elif not with_dot_in_ext:
        file_ext_name = file_ext_name[1:]
    return file_path, file_base_name, file_ext_name


def join_file_path(
    path: str, file_base_name: str, file_type: str = "", suffix: str = "_copy"
) -> str:
    """
    将文件路径、文件基名和文件扩展名结合为完整的文件路径。

        如果文件的完整路径下已存在指定的文件，则在文件名后加“_copy”。

        该方法并不实际创建文件，只是链接文件路径。

    :param path: 文件所在的目录路径。
    :param file_base_name: 文件名（不含扩展名）。
    :param file_type: 文件类型（即文件的扩展名，如果不包含“.”，则自动添加“.”）。
    :param suffix: 后缀，默认为：“_copy”。
    :return: 完整的文件路径。
    """
    # 确保文件类型以点开头。
    if file_type and not file_type.startswith("."):
        file_type = f".{file_type.strip()}"
    # 使用 os.path.join来拼接路径。
    full_path = os.path.join(path, file_base_name + file_type)
    # 循环检查文件是否存在，如果存在则添加后缀。
    while os.path.exists(full_path):
        file_base_name += suffix
        full_path = os.path.join(path, file_base_name + file_type)
    return full_path


def list_files_and_folders(directory: str):
    """
    获取输出指定目录下所有顶级子目录和文件。

    :param directory: 指定的目录。
    :return: (顶级子目录, 顶级文件)
    """
    # 使用os.listdir获取目录下的所有条目
    entries = os.listdir(directory)
    folders = [
        entry for entry in entries if os.path.isdir(os.path.join(directory, entry))
    ]
    files = [
        entry for entry in entries if not os.path.isdir(os.path.join(directory, entry))
    ]
    return folders, files


def print_files_and_folders(directory: str, include_subdirs: bool = True):
    """
    遍历输出指定目录下所有子目录和文件。

    :param directory: 指定的目录。
    :param include_subdirs: 是否包含子目录中的文件，默认为 True。
    """
    if include_subdirs:
        # 使用os.walk遍历目录
        for root, dirs, files in os.walk(directory):
            print(f"Directory: {root}")
            print("Subdirectories:")
            for __dir in dirs:
                print(f"\t{__dir}")
            print("Files:")
            for file in files:
                print(f"\t{file}")
            print("-" * 40)
    else:
        # 使用os.listdir获取目录下的所有条目
        entries = os.listdir(directory)

        # 打印目录名
        print(f"Directory: {directory}")

        # 分别打印文件和文件夹
        print("Top-level directories and files:")
        for entry in entries:
            path = os.path.join(directory, entry)
            if os.path.isdir(path):
                print(f"\tDirectory: {entry}")
            else:
                print(f"\tFile: {entry}")


def list_files_with_suffix(
    suffix: str = ".csv", path: Optional[str] = None, include_subdirs: bool = True
) -> List[str]:
    """
    列出指定路径下（可选包括所有子目录）具有指定后缀名的所有文件。

    :param suffix: 指定的文件后缀名。
    :param path: 指定的路径，默认为当前工作目录。
    :param include_subdirs: 是否包含子目录中的文件，默认为 True。
    :return: 文件列表。
    :rtype: List[str]
    """
    if path is None:
        path = os.getcwd()
    path = os.path.abspath(path)
    # 如果给定的路径是一个文件，则取其所在目录作为新的路径
    if os.path.isfile(path):
        path = os.path.dirname(path)
    # print(path)
    matching_files = []
    from fnmatch import fnmatch

    if include_subdirs:
        # 递归地遍历指定路径及其子目录
        for root, dirs, files in os.walk(path):
            for file in files:
                if fnmatch(file, f"*{suffix}"):
                    matching_files.append(os.path.join(root, file))
    else:
        # 只遍历指定路径下的文件
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path) and fnmatch(file, f"*{suffix}"):
                matching_files.append(file_path)
    return matching_files


def get_project_path():
    """
    获取项目的根目录。

        对于gxusthjw-pythons项目而言,返回结果为：
        `~\\\\gxusthjw-pythons`，这里`~`表示项目所在目录的路径。

    :return: 项目的根目录。
    """
    from pathlib import Path

    return str(Path(__file__).parent.parent.parent.parent.parent.absolute())


def get_root_path():
    """
    获取gxusthjw包的根目录。

        对于gxusthjw-pythons项目而言,返回结果为：
        `~\\\\gxusthjw-pythons\\\\Packages\\\\package-gxusthjw\\\\gxusthjw`

    :return: gxusthjw包的根目录。
    """
    from pathlib import Path

    return str(Path(__file__).parent.parent.absolute())


def get_this_path():
    """
    获取此文件所在文件夹的路径。

        对于gxusthjw-pythons项目而言,返回结果为：
        `~\\\\gxusthjw-pythons\\\\Packages\\\\package-gxusthjw\\\\gxusthjw\\\\files`

    :return: 此文件所在文件夹的路径。
    """
    return os.path.abspath(os.path.dirname(__file__))
