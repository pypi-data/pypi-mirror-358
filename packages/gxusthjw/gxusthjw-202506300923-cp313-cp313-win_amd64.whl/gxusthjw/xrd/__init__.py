#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.xrd包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .xrd_file import XrdFile
from .xrdml_file import read_xrdml, XrdmlFile
from .raw4_file import read_raw4, Raw4File
from .plain_xrd_file import PlainXrdFile
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with
 `XRD (X-ray Diffraction)`.
"""

__all__ = [
    'XrdFile',
    'read_xrdml',
    'XrdmlFile',
    'read_raw4',
    'Raw4File',
    'PlainXrdFile',
]
# 定义 ============================================================
