#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.nmr包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/17     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .bruker_nmr import (
    read_bruker,
    read_pdata_bruker,
    ppm_intensity_bruker,
    NmrBruker
)

from .nmr_c13_spectrum import (
    NmrC13Spectrum,
)

from .nmr_c13_fibroin_spectrum import (
    NmrC13FibroinSpectrum
)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with 
`NMR (Nuclear Magnetic Resonance)`.
"""

__all__ = [
    'read_bruker',
    'read_pdata_bruker',
    'ppm_intensity_bruker',
    'NmrBruker',
    'NmrC13Spectrum',
    'NmrC13FibroinSpectrum',

]
# 定义 ============================================================
