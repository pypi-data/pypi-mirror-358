#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.matplotlibs包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .custom_slider import SliderTextBox
from .matplotlib_utils import (
    import_mpl,
    create_mpl_ax,
    create_mpl_fig
)
from .cross_hair_cursor import (
    TrackableDataCursor,
    select_point_from,
)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with `Matplotlib`.
"""

__all__ = [
    'SliderTextBox',
    'import_mpl',
    'create_mpl_ax',
    'create_mpl_fig',
    'TrackableDataCursor',
    'select_point_from',
]
# 定义 ============================================================
