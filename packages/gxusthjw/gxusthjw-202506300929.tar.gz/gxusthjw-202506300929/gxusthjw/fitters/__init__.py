#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.fitters包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/02     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .sm_linear_fittings import (linear_fitting_sm_rlm,
                                 linear_fitting_sm_ols,
                                 linear_fitting_sm)
from .sm_linear_fitters import (static_linear_fitting_sm,
                                interactive_linear_fitting_sm)
from .data_2d_region_view_sm_linear_fitter import (
    Data2dRegionViewSmLinearFitter)
from .data_2d_region_sm_linear_fitter import (
    Data2dRegionSmLinearFitter)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with `Fitter`.
"""

__all__ = [
    'linear_fitting_sm_rlm',
    'linear_fitting_sm_ols',
    'linear_fitting_sm',
    'static_linear_fitting_sm',
    'interactive_linear_fitting_sm',
    'Data2dRegionViewSmLinearFitter',
    'Data2dRegionSmLinearFitter',
]
# 定义 ============================================================
