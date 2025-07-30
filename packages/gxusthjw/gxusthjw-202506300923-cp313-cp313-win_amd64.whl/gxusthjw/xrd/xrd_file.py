#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        xrd_file.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`XRD数据文件`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
import abc
from typing import (
    Union, Optional, Tuple
)
import numpy as np
import numpy.typing as npt

from ..commons import (
    FileInfo, FileObject, info_of
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `XRD data file`.
"""

__all__ = [
    'XrdFile',
]


# 定义 ==============================================================

class XrdFile(FileObject):
    """
    类`XrdFile`表征“XRD数据文件”。
    """

    def __init__(self, file: Union[str, FileInfo],
                 encoding: Optional[str] = None,
                 **kwargs):
        """
        类`XrdFile`的初始化方法。

        :param file: 文件的完整路径或文件信息（FileInfo）对象。
        :param encoding: 文件编码。
        :param kwargs: 其他可选关键字参数，这些参数全部转化为对象的属性。
        """
        super(XrdFile, self).__init__(file, encoding, **kwargs)
        self.__theta2 = None
        self.__intensity = None

    @abc.abstractmethod
    def read(self, *args, **kwargs) -> Tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        """
        读取数据文件。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 角度和强度数据。
        """
        pass

    @property
    def theta2(self) -> Optional[npt.NDArray[np.float64]]:
        """
        返回2θ数据。

        :return:2θ数据。
        :rtype: Optional[npt.NDArray[np.float64]]
        """
        return self.__theta2

    @property
    def intensity(self) -> Optional[npt.NDArray[np.float64]]:
        """
        返回强度数据。

        :return:强度数据。
        :rtype: Optional[npt.NDArray[np.float64]]
        """
        return self.__intensity

    def _reset_data(self, theta2, intensity):
        """
        重置数据。

        :param theta2: 2θ数据。
        :param intensity: 强度数据。
        :return:
        """
        self.__theta2 = theta2
        self.__intensity = intensity

    def preprocessing(self, **kwargs) -> Tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        """
        对数据进行预处理。

        :param kwargs: 预留的可选关键字参数，以便子类重写该方法。
        :return theta2, intensity
        :rtype:Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]
        """
        if self.__theta2 is None or self.__intensity is None:
            raise ValueError("Please read the data (theta2 and intensity) from the file first.")
        theta2_data = self.__theta2
        intensity_data = self.__intensity

        # 头端被舍弃的数据点数量。
        if 'head_discarded_num_points' in kwargs:
            head_discarded_num_points = kwargs.pop('head_discarded_num_points')
            if head_discarded_num_points is not None and head_discarded_num_points > 0:
                theta2_data = theta2_data[head_discarded_num_points:]
                intensity_data = intensity_data[head_discarded_num_points:]

        # 尾端被舍弃的数据点数量。
        if 'tail_discarded_num_points' in kwargs:
            tail_discarded_num_points = kwargs.pop('tail_discarded_num_points')
            if tail_discarded_num_points is not None and tail_discarded_num_points > 0:
                theta2_data = theta2_data[:-tail_discarded_num_points]
                intensity_data = intensity_data[:-tail_discarded_num_points]

        # theta2保留的数据位数，若为None,则不进行四舍五入运算。
        if 'theta2_round' in kwargs:
            theta2_round = kwargs.pop('theta2_round')
            if theta2_round is not None:
                theta2_data = np.round(theta2_data, decimals=theta2_round)

        if 'reset_data' in kwargs:
            if kwargs.pop('reset_data'):
                self.__theta2 = theta2_data
                self.__intensity = intensity_data

        return theta2_data, intensity_data

    # noinspection PyUnusedLocal
    def to_file(self, out_file: Optional[Union[str, FileInfo]] = None,
                **kwargs):
        """
        输出数据至文件。

        :param kwargs: 预留的可选关键字参数，以便子类重写该方法。
        :param out_file: 输出文件的完整路径。
        """
        if self.__theta2 is None or self.__intensity is None:
            raise ValueError("Please read the data (theta2 and intensity) from the file first.")
        theta2_data = self.__theta2
        intensity_data = self.__intensity
        data_length = len(theta2_data)

        # 保存文件时数据间的分隔符。
        if 'separator' in kwargs:
            separator = kwargs.pop('separator')
        else:
            separator = "\t"

        if separator is None:
            separator = "\t"

        if out_file is None:
            if separator.__eq__("\t"):
                out_file_info = info_of(os.path.join(self.file_directory_path, self.file_base_name + ".raw"))
            else:
                out_file_info = info_of(os.path.join(self.file_directory_path, self.file_base_name + ".txt"))
        else:
            if isinstance(out_file, str):
                out_file_info = info_of(out_file)
            elif isinstance(out_file, FileInfo):
                out_file_info = out_file
            else:
                raise TypeError("out_file must be str or FileInfo")
        out_file_info.make_file()
        with open(out_file_info.full_path, "w") as file:
            for i in range(data_length):
                file.write(str(theta2_data[i]) + separator + str(intensity_data[i]) + "\n")
# ==============================================================================
