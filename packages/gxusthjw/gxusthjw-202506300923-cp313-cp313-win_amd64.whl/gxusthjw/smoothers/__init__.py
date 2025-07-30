#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.smoothers包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/02     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .data_2d_region_smoother import Data2dRegionSmoother
from .data_2d_region_view_smoother import Data2dRegionViewSmoother
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with `Smoother`.
"""

__all__ = [
    "Data2dRegionSmoother",
    "Data2dRegionViewSmoother",
]
# 定义 ============================================================
