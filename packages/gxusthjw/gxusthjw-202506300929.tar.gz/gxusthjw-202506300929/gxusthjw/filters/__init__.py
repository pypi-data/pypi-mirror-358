#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.filters包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/02     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .savgol_filters import (
    simple_interactive_savgol_filter,
    all_interactive_savgol_filter,
    interactive_savgol_filter,
    static_savgol_filter,
)
from .data_2d_region_savgol_filters import (
    Data2dRegionSavgolFilter
)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with `Filter`.
"""

__all__ = [
    "simple_interactive_savgol_filter",
    "all_interactive_savgol_filter",
    "interactive_savgol_filter",
    "static_savgol_filter",
    "Data2dRegionSavgolFilter",
]
# 定义 ============================================================
