#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.ftir包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/02     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .ftir_at_conversion import (
    absorbance_to_transmittance, absorbance_to_transmittance2,
    transmittance_to_absorbance, transmittance_to_absorbance2
)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with 
`FTIR (Fourier Transform Infrared Spectroscopy)`.
"""

__all__ = [
    'transmittance_to_absorbance',
    'absorbance_to_transmittance',
    'transmittance_to_absorbance2',
    'absorbance_to_transmittance2',
]
# 定义 ============================================================
