#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        folder_operator.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“文件夹”相关函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/17     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import logging
import os
import shutil
from typing import Optional, Literal, Union, List, Dict
from pathlib import Path

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define functions and classes associated with 'folder'.
"""

__all__ = [
    'folder_cleanup',
    'folder_create'
]

# 定义 ==============================================================
logger = logging.getLogger(__name__)


def folder_cleanup(
        folder_path: Union[str, Path],
        target_type: Optional[Literal["dir", "file", "both"]] = 'both'
):
    """
    删除指定文件夹下的子目录和/或文件。

    :param folder_path: 要处理的文件夹路径。
    :param target_type: 指定要删除的内容类型。可选值有：
                        'dir' - 仅删除目录。
                        'file' - 仅删除文件。
                        'both' - 同时删除目录和文件。
    """
    # 将传入的路径转换为绝对路径，确保后续操作的准确性
    folder_path = Path(folder_path).resolve()

    # 检查路径是否存在，如果不存在则抛出异常
    if not folder_path.exists():
        raise ValueError(f"Path {folder_path} does not exist.")

    # 定义合法的 target_type 类型列表
    valid_types = ['dir', 'file', 'both']
    # 检查 target_type 是否合法，如果不合法则抛出异常
    if target_type not in valid_types:
        raise ValueError(f"Invalid target_type: '{target_type}'. "
                         f"Valid options are {valid_types}")

    # 遍历文件夹下的所有项目
    for item in folder_path.iterdir():
        try:
            # 如果项目是目录
            if item.is_dir():
                # 如果 target_type 包含目录，则删除该目录
                if target_type in ('dir', 'both'):
                    # 防止符号链接造成的误删
                    if item.is_symlink():
                        logger.warning(f"Skipped symlink directory: {item}")
                        continue
                    shutil.rmtree(item)
            else:
                # 如果项目是文件
                if target_type in ('file', 'both'):
                    # 处理 Windows 下只读文件
                    if os.name == 'nt':
                        os.chmod(item, 0o777)
                    item.unlink()
        except Exception as e:
            # 记录删除过程中遇到的任何异常
            logger.error(f"Failed to delete {item}: {e}", exc_info=True)


def folder_create(folder_path: Union[str, Path],
                  folders: Union[List[str], None] = None,
                  files: Union[Dict[str, str], None] = None):
    """
    在指定路径下创建文件夹和文件，并支持多种编码格式。

    :param folder_path: 基础文件夹路径。
    :param folders: 要创建的子文件夹名称列表。
    :param files: dict，键为文件名，值可以是：
                  - 字符串：表示文件内容，默认使用 'utf-8' 编码。
                  - 字典：格式为 {'content': '...', 'encoding': '...'}，自定义编码。
    """
    base_path = Path(folder_path)

    # 创建基础目录
    try:
        base_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Unable to create base path {base_path}: {e}")

    # 创建子文件夹
    if folders:
        for folder in folders:
            sub_folder_path = base_path / folder
            try:
                sub_folder_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Unable to create subfolder {sub_folder_path}: {e}")

    # 创建文件并指定编码
    if files:
        for filename, content_info in files.items():
            file_path = base_path / filename
            encoding = 'utf-8'

            if isinstance(content_info, dict):
                content = content_info.get('content', '')
                encoding = content_info.get('encoding', 'utf-8')
            else:
                content = content_info

            try:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
            except (IOError, OSError) as e:
                logger.error(f"Unable to write file {file_path}: {e}")
# ==================================================================
