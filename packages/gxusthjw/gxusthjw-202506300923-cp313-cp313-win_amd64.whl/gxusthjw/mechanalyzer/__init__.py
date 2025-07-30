#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.mechanalyzer包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/02     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .unit_convert import (
    length_unit_to_mm,
    time_unit_to_s,
    force_unit_to_cn,
    area_unit_to_mm2,
    speed_unit_to_mms,
)
from .cre_datalyzer import (
    CreMechDataAnalyzer
)
from .pootab_pt1198gdp import (
    PootabPt1198Gdp,
)

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with 
`Mechanical Data Analyzer`.
"""

__all__ = [
    "length_unit_to_mm",
    "force_unit_to_cn",
    "area_unit_to_mm2",
    "time_unit_to_s",
    "speed_unit_to_mms",
    "CreMechDataAnalyzer",
    'PootabPt1198Gdp',
]
# 定义 ============================================================
