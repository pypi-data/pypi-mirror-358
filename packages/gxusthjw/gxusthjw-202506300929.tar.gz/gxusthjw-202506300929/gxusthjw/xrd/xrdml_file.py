#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        xrdml_file.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      处理“.xrdml格式的XRD数据”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
import xml.dom.minidom
from typing import (
    Optional, Tuple, Union, override
)

import numpy as np
import numpy.typing as npt

from .xrd_file import (
    XrdFile,
)

from ..commons import (
    FileInfo, info_of
)

# 定义 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Processing xrd data file with .xrdml format.
"""

__all__ = [
    'read_xrdml',
    'XrdmlFile',
]


# ==================================================================

def read_xrdml(xrdml_file: Union[str, FileInfo],
               head_discarded_num_points: Optional[int] = None,
               tail_discarded_num_points: Optional[int] = None,
               theta2_round: Optional[int] = None,
               is_out_file: Optional[bool] = False,
               separator: Optional[str] = None,
               out_file: Optional[Union[str, FileInfo]] = None) -> Tuple[
    npt.NDArray[np.float64], npt.NDArray[np.float64]
]:
    """
    读取并解析.xrdml格式的XRD数据文件。

        注意：

            1. 如果参数is_out_file为True，而参数out_file为None时，
               输出文件的目录路径与参数xrdml_file的目录路径相同，
               当参数separator为None或"\t"时，输出为.raw文件，
               否则输出为.txt格式的文件。

    :param xrdml_file: .xrdml格式XRD数据文件的完整路径。
    :param head_discarded_num_points: 头端被舍弃的数据点数量。
    :param tail_discarded_num_points: 尾端被舍弃的数据点数量。
    :param theta2_round: theta2保留的数据位数，若为None,则不进行四舍五入运算。
    :param is_out_file: 指示是否输出数据文件，若为True，则输出，若为False，则不输出。
    :param separator: 保存文件的分隔符。
    :param out_file: 输出文件的完整路径。
    :return theta2, intensity
    :rtype:Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]
    """
    # 读取数据 =========================================================
    if isinstance(xrdml_file, str):
        xrdml_file_info = info_of(xrdml_file)
    elif isinstance(xrdml_file, FileInfo):
        xrdml_file_info = xrdml_file
    else:
        raise TypeError("xrdml_file must be str or FileInfo")

    # 解析 XML
    try:
        dom = xml.dom.minidom.parse(str(xrdml_file_info.full_path))
    except Exception as e:
        raise RuntimeError(f"Failed to parse XML file '{xrdml_file_info.full_path}': {e}")

    root = dom.documentElement
    position_data = root.getElementsByTagName('positions')
    # 读取角度数据。
    theta2_start = None
    theta2_end = None
    for position_node in position_data:
        if position_node.getAttribute('axis') == "2Theta":
            theta2 = position_node.getElementsByTagName("startPosition")
            theta2_start = theta2[0].firstChild.data
            theta2_start = float(theta2_start)
            theta2 = position_node.getElementsByTagName("endPosition")
            theta2_end = theta2[0].firstChild.data
            theta2_end = float(theta2_end)
    # 读取强度数据。
    intensity = root.getElementsByTagName('intensities')
    intensity_str = intensity[0].firstChild.data
    intensity_str_split = intensity_str.split()
    n = len(intensity_str_split)
    theta2_data = np.linspace(theta2_start, theta2_end, n, dtype=np.float64, endpoint=True)
    intensity_data = np.array([int(s) for s in intensity_str_split], dtype=np.int32)

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
                    os.path.join(xrdml_file_info.dir_path, xrdml_file_info.base_name + ".raw"))
            else:
                out_file_info = info_of(
                    os.path.join(xrdml_file_info.dir_path, xrdml_file_info.base_name + ".txt"))
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


# ==============================================================================
class XrdmlFile(XrdFile):
    """
    类`XrdmlFile`表征“.xrdml格式的XRD数据”。
    """

    def __init__(self, file: Union[str, FileInfo],
                 encoding: Optional[str] = None,
                 **kwargs):
        """
        类`XrdmlFile`的初始化方法。

        :param file: 文件的完整路径或文件信息（FileInfo）对象。
        :param encoding: 文件编码。
        :param kwargs: 其他可选关键字参数，这些参数全部转化为对象的属性。
        """
        super(XrdmlFile, self).__init__(file, encoding, **kwargs)

    @override
    def read(self, reset_data: bool = False) -> Tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        """
        读取数据文件。

        :param reset_data: 是否重置对象内部数据。
        :return theta2, intensity
        :rtype:Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]
        """
        dom = xml.dom.minidom.parse(str(self.file_full_path))
        root = dom.documentElement
        data = root.getElementsByTagName('positions')
        theta2_start = 0
        theta2_end = 1
        for i in data:
            # print(i.getAttribute('axis'))
            if i.getAttribute('axis') == "2Theta":
                theta2 = i.getElementsByTagName("startPosition")
                theta2_start = theta2[0].firstChild.data
                theta2_start = float(theta2_start)
                theta2 = i.getElementsByTagName("endPosition")
                theta2_end = theta2[0].firstChild.data
                theta2_end = float(theta2_end)

        intensity = root.getElementsByTagName('intensities')
        intensity_str = intensity[0].firstChild.data
        intensity_str_data = intensity_str.split()
        n = len(intensity_str_data)

        theta2_data = np.linspace(theta2_start, theta2_end, n, dtype=np.float64, endpoint=True)
        intensity_data = np.array([int(s) for s in intensity_str_data], dtype=np.int32)

        if reset_data:
            self._reset_data(theta2_data, intensity_data)

        return theta2_data, intensity_data

# ==============================================================================
