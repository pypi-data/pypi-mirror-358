#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        raw4_file.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      处理“.raw4.00格式的XRD数据”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
from typing import (
    Union, Optional, Tuple,override
)

import numpy as np
import numpy.typing as npt
import pandas as pd
from ..commons import (
    FileInfo, info_of
)
from .xrd_file import (
    XrdFile,
)
# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Processing xrd data file with .raw4.00 format.
"""

__all__ = [
    'read_raw4',
    'Raw4File',
]


# 定义 ==============================================================

def read_raw4(raw4_file: Union[str, FileInfo],
              head_discarded_num_points: Optional[int] = None,
              tail_discarded_num_points: Optional[int] = None,
              theta2_round: Optional[int] = None,
              is_out_file: Optional[bool] = False,
              separator: Optional[str] = None,
              out_file: Optional[Union[str, FileInfo]] = None) -> Tuple[
    npt.NDArray[np.float64], npt.NDArray[np.float64]
]:
    """
    读取并解析.raw4.00格式的XRD数据文件。

    :param raw4_file: .raw4.00格式XRD数据文件的完整路径。
    :param head_discarded_num_points: 头端被舍弃的数据点数量。
    :param tail_discarded_num_points: 尾端被舍弃的数据点数量。
    :param theta2_round: theta2保留的数据位数，若为None,则不进行四舍五入运算。
    :param is_out_file: 指示是否输出数据文件，若为True，则输出，若为False，则不输出。
    :param separator: 保存文件的分隔符。
    :param out_file: 输出文件的完整路径。
    :return theta2, intensity
    :rtype:Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]
    """
    if isinstance(raw4_file, str):
        raw4_file_info = info_of(raw4_file)
    elif isinstance(raw4_file, FileInfo):
        raw4_file_info = raw4_file
    else:
        raise TypeError("The type of raw4_file must be str or FileInfo")

    # 打开文件
    with open(raw4_file_info.full_path, 'r', encoding=raw4_file_info.encoding) as file:
        # 读取所有行。
        lines = file.readlines()

    # 查找[data]的位置
    start_index = -1
    for i, line in enumerate(lines):
        if line.strip().lower() == '[data]':
            start_index = i + 1  # 跳过[data]这一行
            break

    if start_index < 0:
        raise ValueError("The [data] tag was not found")

    # 读取第一行的列名
    column_names = [f"{raw4_file_info.base_name}_{col.strip()}" for col in lines[start_index].split(',') if col.strip()]
    print(column_names)
    # 去除空行或只包含空格的行，并且去除每行末尾的空字符串
    data_lines = [
        [float(item.strip()) for item in line.strip().split(',') if item]  # 过滤掉空字符串
        for line in lines[start_index + 1:]
        if line.strip()  # 只处理非空行
    ]
    print(data_lines)
    # 创建DataFrame
    df = pd.DataFrame(data=data_lines, columns=column_names)
    theta2_data = np.asarray(df[column_names[0]])
    intensity_data = np.asarray(df[column_names[1]])

    # 对数据进行预处理。
    if head_discarded_num_points is not None and head_discarded_num_points > 0:
        theta2_data = theta2_data[head_discarded_num_points:]
        intensity_data = intensity_data[head_discarded_num_points:]
    if tail_discarded_num_points is not None and tail_discarded_num_points > 0:
        theta2_data = theta2_data[:-tail_discarded_num_points]
        intensity_data = intensity_data[:-tail_discarded_num_points]

    if theta2_round is not None:
        theta2_data = np.round(theta2_data, decimals=theta2_round)

    # 输出数据至文件。
    if is_out_file:
        if separator is None:
            separator = "\t"
        if out_file is None:
            if separator.__eq__("\t"):
                out_file_info = info_of(
                    os.path.join(raw4_file_info.directory_path, raw4_file_info.base_name + ".raw"))
            else:
                out_file_info = info_of(
                    os.path.join(raw4_file_info.directory_path, raw4_file_info.base_name + ".txt"))
        else:
            if isinstance(out_file, str):
                out_file_info = info_of(out_file)
            elif isinstance(out_file, FileInfo):
                out_file_info = out_file
            else:
                raise TypeError("out_file must be str or FileInfo")

        data_length = len(theta2_data)
        out_file_info.make_file()
        with open(out_file_info.full_path, "w") as file:
            for d in range(data_length):
                file.write(str(theta2_data[d]) + separator + str(intensity_data[d]) + "\n")

    return theta2_data, intensity_data


class Raw4File(XrdFile):
    """
    类`Raw4File`表征“.raw4.00格式的XRD数据”。
    """

    def __init__(self, file: Union[str, FileInfo],
                 encoding: Optional[str] = None,
                 **kwargs):
        """
        类`Raw4File`的初始化方法。

        :param file: 文件的完整路径或文件信息（FileInfo）对象。
        :param encoding: 文件编码。
        :param kwargs: 其他可选关键字参数，这些参数全部转化为对象的属性。
        """
        super(Raw4File, self).__init__(file, encoding, **kwargs)

    @override
    def read(self, reset_data: bool = False) -> Tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        """
        读取数据文件。

        :param reset_data: 是否重置对象内部数据。
        :return theta2, intensity
        :rtype:Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]
        """
        # 打开文件
        with open(self.file_full_path, 'r', encoding=self.encoding) as file:
            # 读取所有行。
            lines = file.readlines()

        # 查找[data]的位置
        start_index = -1
        for i, line in enumerate(lines):
            if line.strip().lower() == '[data]':
                start_index = i + 1  # 跳过[data]这一行
                break

        if start_index < 0:
            raise ValueError("The [data] tag was not found")

        # 读取第一行的列名
        column_names = [f"{self.file_base_name}_{col.strip()}" for col in lines[start_index].split(',') if
                        col.strip()]
        print(column_names)
        # 去除空行或只包含空格的行，并且去除每行末尾的空字符串
        data_lines = [
            [float(item.strip()) for item in line.strip().split(',') if item]  # 过滤掉空字符串
            for line in lines[start_index + 1:]
            if line.strip()  # 只处理非空行
        ]
        print(data_lines)
        # 创建DataFrame
        df = pd.DataFrame(data=data_lines, columns=column_names)
        theta2_data = np.asarray(df[column_names[0]])
        intensity_data = np.asarray(df[column_names[1]])

        if reset_data:
            self._reset_data(theta2_data, intensity_data)

        return theta2_data, intensity_data
# ==============================================================================