#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        plain_xrd_file.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      处理“普通文本格式的XRD数据文件”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import (
    Union, Optional, Tuple, Mapping, override
)
import numpy as np
import numpy.typing as npt

from ..commons import (
    FileInfo, read_txt
)

from .xrd_file import XrdFile

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Processing xrd data file with `plain text` format.
"""

__all__ = [
    'PlainXrdFile',
]


# 定义 ==============================================================
class PlainXrdFile(XrdFile):
    """
    类`PlainXrdFile`表征“普通文本格式的XRD数据文件”。
    """

    def __init__(self, file: Union[str, FileInfo],
                 encoding: Optional[str] = None,
                 **kwargs):
        """
        类`PlainXrdFile`的初始化方法。

        :param file: 文件的完整路径或文件信息（FileInfo）对象。
        :param encoding: 文件编码。
        :param kwargs: 其他可选关键字参数，这些参数全部转化为对象的属性。
        """
        super(PlainXrdFile, self).__init__(file, encoding, **kwargs)

    @override
    def read(self, reset_data: bool = False,
             sep: Optional[str] = None,
             skiprows: int = 0,
             cols: Optional[Mapping[int, Optional[str]]] = None,
             encoding: Optional[str] = None
             ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        """
        读取数据文件。

        :param reset_data: 是否重置对象内部数据。
        :param sep: 数据间的分隔符，如果为None，则以空白符为分割符。
        :param skiprows: 跳过的行数，默认为0。
        :param cols: 指定要读取的列。
        :param encoding: 文件编码，如果文件编码未知，则利用chardet尝试解析，
                        如果未能解析出文件的编码，则以“GBK”读取文件。
        :return theta2, intensity
        :rtype:Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]
        """
        theta2_data, intensity_data = read_txt(
            self.file_full_path,
            sep=sep,
            skiprows=skiprows,
            cols=cols,
            encoding=encoding,
            res_type="list_numpy"
        )
        if reset_data:
            self._reset_data(theta2_data, intensity_data)
        return theta2_data, intensity_data
