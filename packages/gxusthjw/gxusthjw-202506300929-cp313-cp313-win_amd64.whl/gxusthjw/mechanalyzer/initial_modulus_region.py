#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        initial_modulus_region.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与“初始模量区域”相关的函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/09/27     revise
# ------------------------------------------------------------------
# 导包 ============================================================
from typing import Optional

from ..commons import NumberSequence
from ..fitters import Data2dRegionViewSmLinearFitter

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the functions and classes associated with 'initial modulus region'.
"""

__all__ = [
    "InitialModulusRegion",
]


# 定义 ============================================================
class InitialModulusRegion(Data2dRegionViewSmLinearFitter):
    """
    类`InitialModulusRegion`表征“应力应变曲线的初始模量区域”。
    """

    def __init__(
        self,
        stress: NumberSequence,
        strain: Optional[NumberSequence] = None,
        region_start: int = 0,
        region_length: Optional[int] = None,
        view_start: int = 0,
        view_length: Optional[int] = None,
        fitting_method: str = "ols",
    ):
        """
        类`InitialModulusRegion`的初始化方法。

        :param stress: 应力应变曲线的应力数据。
        :param strain: 应力应变曲线的应变数据（可选）。
        :param region_start: 应力应变曲线上初始模量区域的起始索引。
        :param region_length: 应力应变曲线上初始模量区域的长度。
        :param view_start: 应力应变曲线上视图区域的初始索引。
        :param view_length: 应力应变曲线上视图区域的长度。
        :param fitting_method: 拟合方法，只可以 ‘ols’ 或 ‘rlm’ 。
        """
        # -----------------------------------------------------------------
        super(InitialModulusRegion, self).__init__(
            data_y=stress,
            data_x=strain,
            region_start=region_start,
            region_length=region_length,
            view_start=view_start,
            view_length=view_length,
            method=fitting_method,
        )
        # -----------------------------------------------------------------
