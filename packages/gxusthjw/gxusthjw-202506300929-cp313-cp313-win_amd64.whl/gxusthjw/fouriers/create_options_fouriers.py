#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        create_options.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义一个函数，用于创建傅里叶数据处理中所需的配置选项。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/18     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from types import SimpleNamespace

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a function that generates the configuration parameters 
needed in Fourier data processing.
"""

__all__ = [
    'create_options_fouriers',
]


# 定义 ==============================================================
def create_options_fouriers()->SimpleNamespace:
    """
    创建并返回一个包含各种处理选项的对象。
    所有字段含义根据业务需求设定，
    用于控制算法行为。
    """
    options = SimpleNamespace()

    #
    options.InterpolationValues = [
        "16", "8", "4", "2",
        "1", "0.5", "0.25", "0.125"
    ]
    options.Interpolation = 1
    options.DerivativeOrder = 2

    #
    options.CutPoint = 1 / 8
    options.CutPointInverse = 1 / 2
    options.CutPointInverseFactor = 0.98

    #
    options.PhaseCorrection = "On"
    options.PhaseCorrectionType = ["On", "Off"]

    #
    options.FSD_narrowing = 2
    options.FSD_FWHHL = 18
    options.FSD_FWHHG = 0

    #
    options.Filter = "Bessel"
    options.FilterInverse = "Triangle"
    options.FilterType = [
        "Boxcar",
        "Norton-Beer Medium",
        "Triangle",
        "Hamming",
        "Norton-Beer Strong",
        "Bessel",
        "Hanning",
        "Lorentzian",
        "Gaussian",
        "Truncated Gaussian",
        "Sinc-Sq",
        "Blackman",
        "Blackman-Harris 3-term",
        "Blackman-Lorenz 3-term",
        "Triangle-Sq"
    ]

    #
    options.Border = "mirror"
    options.BorderType = [
        "none",
        "mirror",
        "refl-att",
        "refl-inv-att"
    ]
    options.BorderExtension = 100

    #
    options.x_linearityTol = 1e-3

    return options
# ==================================================================
