#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        pdf2png_core.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      PDF2PNG工具的核心代码。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/15     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import pymupdf
import os
import warnings
from pathlib import Path

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
The core code of the PDF2PNG tool.
"""

__all__ = [
    'mkdir',
    'pdf2img',

]

# 定义 ==============================================================
# 忽略弃用警告，防止控制台输出干扰信息。
warnings.filterwarnings(
    "ignore", category=DeprecationWarning,
    message="builtin type swigvarlink has no __module__ attribute"
)


def mkdir(path: str | Path,
          file_base_name: str, file_ext_name: str = '',
          max_attempts: int = 1000,
          create_dir: bool = False) -> str:
    """
    生成一个唯一的文件名或目录路径。

    :param path: 文件或目录的路径。
    :param file_base_name: 文件的基本名称，不包括扩展名。
    :param file_ext_name: 文件的扩展名，默认为空。
    :param max_attempts: 尝试生成唯一文件名的最大次数，默认为 1000。
    :param create_dir: 如果为 True 并且文件扩展名为空，则创建目录，默认为 False。
    :return: 一个唯一的文件名或目录路径。
    :raise ValueError: 如果 file_base_name 为空。
    :raise FileExistsError: 如果达到 max_attempts 仍未生成唯一的文件名。
    """
    if not file_base_name:
        raise ValueError("file_base_name cannot be empty")

    # 标准化路径
    normalized_path = os.path.normpath(path)

    # 确保扩展名以 . 开头
    if file_ext_name and not file_ext_name.startswith('.'):
        file_ext_name = '.' + file_ext_name

    counter = 0  # 初始化计数器，用于在文件名已存在时生成不同的文件名
    base_filename = file_base_name  # 保存原始文件名，用于生成备选文件名。

    # 尝试生成唯一的文件名，直到成功或达到最大尝试次数
    while counter < max_attempts:
        # 第一次尝试使用原始文件名，不加后缀
        if counter == 0:
            filename = f"{file_base_name}{file_ext_name}"
        else:
            # 如果文件名已存在，生成带有_copy后缀的文件名
            filename = f"{base_filename}_copy{counter}{file_ext_name}"

        full_path = os.path.join(normalized_path, filename)

        # 检查是否存在
        if not os.path.exists(full_path):
            if file_ext_name == '' and create_dir:
                os.makedirs(full_path, exist_ok=True)
            return full_path

        counter += 1  # 计数器增加，用于生成下一个备选文件名

    # 如果达到最大尝试次数仍未找到唯一的文件名，抛出异常
    raise FileExistsError(
        f"Unable to generate a unique filename under the path {normalized_path}, "
        f"maximum attempt count {max_attempts} has been reached."
    )


def get_dir_name(file_dir):
    """
    将给定的文件路径拆分为目录路径和文件名。

    :param file_dir: 文件路径字符串。
    :return: 包含两个元素的元组 (目录路径, 文件名)。
    :raise TypeError: 如果输入不是字符串类型。
    :raise ValueError: 如果输入为空字符串或无效路径。
    """
    base_name = os.path.basename(file_dir)  # 获取路径中的文件名部分
    dir_name = os.path.dirname(file_dir)  # 获取路径中的目录部分
    return dir_name, base_name


def pdf2img(pdf_file, zoom=2, out_format="png", out_path: str | Path = None):
    """
    将PDF文件转换为图像文件。

    :param pdf_file: PDF文件的完整路径。
    :param zoom: 放大倍数，用于控制输出图像的分辨率。
    :param out_path: 文件输出的路径。
    :param out_format: 输出图像的格式，可以是'png'或'jpg'。
    :return: 转换成功返回True，否则返回False。
    """
    # 检查放大倍数是否有效
    if zoom <= 0:
        raise ValueError("Zoom factor must be greater than zero.")

    # 检查输出格式是否有效
    if out_format not in ('png', 'jpg'):
        raise ValueError("Output format must be either 'png' or 'jpg'.")

    # 提取路径和基础文件名
    file_path, file_name = os.path.split(pdf_file)
    base_name, ext = os.path.splitext(file_name)

    if ext != '.pdf':
        raise ValueError()

    if out_path is None:
        out_path = mkdir(file_path, base_name)
    else:
        out_path = mkdir(out_path, base_name)

    os.makedirs(out_path, exist_ok=True)

    output_dir = Path(out_path)
    output_prefix = output_dir / base_name

    try:
        # 打开PDF文件
        with pymupdf.open(pdf_file) as pdf:
            # 遍历每一页PDF
            for pg_num in range(pdf.page_count):
                page = pdf[pg_num]
                # 创建矩阵用于放大页面
                trans = pymupdf.Matrix(zoom, zoom)
                # 将页面转换为像素映射
                # noinspection PyUnresolvedReferences
                pm = page.get_pixmap(matrix=trans, alpha=False)

                # 构造输出文件路径
                output_path = f"{output_prefix}_{pg_num:04d}.{out_format}"

                # 根据指定的格式保存图像
                if out_format == 'png':
                    pm.save(output_path, "png")
                elif out_format == 'jpg':
                    pm.save(output_path, "jpeg")

        # 转换成功
        return True
    except Exception as e:
        # 处理转换过程中的异常
        print(f"An error occurred during PDF to image conversion: {e}")
        # 转换失败
        return False
