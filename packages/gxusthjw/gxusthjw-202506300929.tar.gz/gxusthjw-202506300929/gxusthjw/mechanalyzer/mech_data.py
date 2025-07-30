#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        mech_data.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义表征`力学数据`的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/29     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from ..commons import (
    Specimen
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents `mechanical data`.
"""

__all__ = [
    'MechanicalData',
]


# 定义 ==============================================================

class MechanicalData(Specimen):
    """
    类`MechanicalData`表征“力学数据”。
    """

    def __init__(self, *args, **kwargs):
        """
        类`MechanicalData`的初始化方法。

            该初始化方法未进行任何处理，仅仅是对Specimen的简单继承。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        """
        super(MechanicalData, self).__init__(*args, **kwargs)

# ==================================================================