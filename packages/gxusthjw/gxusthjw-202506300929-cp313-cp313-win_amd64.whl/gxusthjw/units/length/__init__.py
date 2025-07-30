#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.units.length包的__init__.py。
#                   承载“表征`长度`”的计量单位。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/10/02     revise
#       Jiwei Huang        0.0.1         2024/09/12     revise
# ------------------------------------------------------------------
# 导包 =============================================================
from .length_unit_base import (LengthUnit,
                               MetricLengthUnit,
                               Kilometer,
                               Meter,
                               Decimeter,
                               Centimeter,
                               Millimeter,
                               Micrometer,
                               Nanometer,
                               Picometer,
                               Angstrom,
                               km,
                               m,
                               dm,
                               cm,
                               mm,
                               µm,
                               nm,
                               pm,
                               Å)

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the classes and functions associated with `length unit`.
"""

__all__ = [
    'LengthUnit',
    'MetricLengthUnit',
    'Kilometer',
    'Meter',
    'Decimeter',
    'Centimeter',
    'Millimeter',
    'Micrometer',
    'Nanometer',
    'Picometer',
    'Angstrom',
    'km',
    'm',
    'dm',
    'cm',
    'mm',
    'µm',
    'nm',
    'pm',
    'Å'
]
# ==================================================================
