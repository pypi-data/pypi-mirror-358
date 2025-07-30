#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.zhxyao.cython包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .deriv_gl_cy import (
    deriv_gl_cy,
    deriv_gl_cy_0,
)

from .quasi_sech_cy import (
    sech_cy,
    sech_cy_0,
    quasi_sech_cy,
)

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembles classes and functions associated with `zhxyao` 
using `cython`.
"""

__all__ = [
    'deriv_gl_cy',
    'deriv_gl_cy_0',
    'sech_cy',
    'sech_cy_0',
    'quasi_sech_cy',
]
# 定义 ============================================================
