#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.statistics包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .residuals_analysis import Residuals
from .fitting_statistics import (
    rsquared,
    chisqr,
    chisqr_p,
    redchi,
    aic,
    bic,
    FittingStatistics
)

from .finite_normal_distribution import (
    finite_norm_pdf,
    finite_norm_cdf_od,
    finite_norm_cdf,
    FiniteNormalDistribution,
    finite_norm
)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with `Statistics`.
"""

__all__ = [
    'Residuals',
    'rsquared',
    'chisqr',
    'chisqr_p',
    'redchi',
    'aic',
    'bic',
    'FittingStatistics',
    'finite_norm_pdf',
    'finite_norm_cdf_od',
    'finite_norm_cdf',
    'FiniteNormalDistribution',
    'finite_norm',
]
# 定义 ============================================================
