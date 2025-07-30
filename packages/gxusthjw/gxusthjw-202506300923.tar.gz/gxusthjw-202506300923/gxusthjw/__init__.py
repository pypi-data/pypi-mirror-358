#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     revise
# ----------------------------------------------------------------
# 导包 ==============================================================
from . import axs
from . import commons
from . import filters
from . import findpeaks
from . import fitters
from . import fityks
from . import fouriers
from . import fsd
from . import ftir
from . import mathematics
from . import matlabs
from . import matplotlibs
from . import mechanalyzer
from . import mestrenovas
from . import nmr
from . import omnics
from . import originpros
from . import pdf2png
from . import peakfits
from . import smoothers
from . import spectrum
from . import statistics
from . import units
from . import xrd
from . import zhxyao

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
the python packages of gxusthjw.
"""

__all__ = [
    'run_tests',
    'axs',
    'commons',
    'filters',
    'findpeaks',
    'fitters',
    'fityks',
    'fouriers',
    'fsd',
    'ftir',
    'mathematics',
    'matlabs',
    'matplotlibs',
    'mechanalyzer',
    'mestrenovas',
    'nmr',
    'omnics',
    'originpros',
    'pdf2png',
    'peakfits',
    'smoothers',
    'spectrum',
    'statistics',
    'units',
    'xrd',
    'zhxyao',
]


# 定义 ============================================================
def run_tests():
    """
    运行此包及其子包中的所有测试。

        运行方式：
            > import gxusthjw
            > gxusthjw.run_tests()
    """
    import unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('.')
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)
# ==================================================================
