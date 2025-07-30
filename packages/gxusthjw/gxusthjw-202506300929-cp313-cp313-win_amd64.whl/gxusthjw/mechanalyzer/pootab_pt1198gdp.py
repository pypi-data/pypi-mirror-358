#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        pootab_pt1198gdp.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`POOTAB-PT1198GDP拉伸仪输出文件`”的类。
#                   POOTAB是东莞市宝大仪器有限公司的产品商标，
#                   PT1198GDP是东莞市宝大仪器有限公司出品的
#                   一款小型力学测试仪器。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/08/23     revise
#       Jiwei Huang        0.0.1         2025/06/28     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import (
    Union, Optional
)
import numpy as np
import pandas as pd
from pathlib import Path
from .cre_datalyzer import CreMechDataAnalyzer
from ..commons import FileObject, FileInfo

# 定义 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines a class that represents ‘output file of POOTAB-PT1198GDP
 tensioner’.
"""
__all__ = [
    'PootabPt1198Gdp'
]


# ==================================================================

class PootabPt1198Gdp(FileObject):
    """
    类`PootabPt1198Gdp`表征“POOTAB-PT1198GDP拉伸仪输出的文件”。

    POOTAB是东莞市宝大仪器有限公司的产品商标。

    PT1198GDP是东莞市宝大仪器有限公司出品的一款小型力学测试仪器。
    """

    def __init__(self, file: Union[str, FileInfo,Path],
                 encoding: Optional[str] = None,
                 **kwargs):
        """
        类`PootabPt1198Gdp`的初始化方法。

        :param file: 文件的路径或文件信息对象。
        :param encoding: 文件编码。
        :param kwargs: 其他可选关键字参数，这些参数全部转化为对象的属性。
        """
        super(PootabPt1198Gdp, self).__init__(file, encoding, **kwargs)

    # noinspection PyAttributeOutsideInit
    def read_data(self, **kwargs) -> pd.DataFrame:
        """
        读取力学数据文件。

        :param kwargs: 读取文件所需的关键字参数。
        :return: pd.DataFrame对象。
        """
        # ----------------------------------------
        # 是否将读取到的数据通过print输出。
        is_print = kwargs.pop("is_print", False)
        # ----------------------------------------
        if hasattr(self, 'data'):
            data = self.data
        else:
            # 读取数据
            if not (self.file_ext_name == "xls" or self.file_ext_name == "xlsx"):
                raise ValueError("Expect a file with .xls or.xlsx suffix.")
            data = pd.read_excel(self.file_full_path, header=0, engine='openpyxl')
            setattr(self, 'data', data)
        # ----------------------------------------
        # 打印数据。
        if is_print:
            print(data)
        # ----------------------------------------
        return data

    def get_datalyzer(self, **kwargs):
        """
        获取力学数据分析器。

        :param kwargs: 所需的关键字参数。
        :return:力学数据分析器。
        """
        # 是否将读取到的数据通过print输出。
        is_print = kwargs.pop("is_print", False)
        data = self.read_data(is_print=is_print)
        nos = np.asarray(data.iloc[:, 0], dtype=np.int64)
        times = np.asarray(data.iloc[:, 1], dtype=np.float64)
        displacements = np.asarray(data.iloc[:, 2], dtype=np.float64)
        forces = np.asarray(data.iloc[:, 3], dtype=np.float64)
        assert np.allclose(np.arange(1, nos.shape[0] + 1), nos)
        return CreMechDataAnalyzer(displacements, forces, times, **kwargs)
# ====================================================================
