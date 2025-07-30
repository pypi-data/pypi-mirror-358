#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.zhxyao包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ----------------------------------------------------------------
# 导包 ============================================================
from .deriv_gl import (
    deriv_gl,
)
from .cython import (
    deriv_gl_cy,
    deriv_gl_cy_0,
    sech_cy,
    sech_cy_0,
    quasi_sech_cy,
)

from .quasi_sech import (
    sech,
    sech_np,
    quasi_sech,
    quasi_sech_np,
)

from .deriv_quasi_sech import (
    quasi_sech_ifft,
    deriv_quasi_sech,
    deriv_quasi_sech_reviews
)
from .deriv_quasi_sech_fp import (
    quasi_sech_ifft_fp,
    deriv_quasi_sech_fp,
    deriv_quasi_sech_fp_reviews
)

from .deriv_quasi_sech_ext import (
    deriv_quasi_sech_fit_steepness,
    deriv_quasi_sech_search_steepness,
)

from .smoothing_zhxyao import (
    smoothing_zhxyao
)
from .arbitrary_deriv_oop import (
    EnvelopeFunction,
    QuasiSechEnvelope,
    GeneralPeakEnvelope,
    ArbitraryOrderDerivativeAlgorithm,
    ArbitraryOrderDerivativeZhxyaoGl,
    ArbitraryOrderDerivative,
)
# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling classes and functions associated with `zhxyao`.
"""

__all__ = [
    'deriv_gl',
    'deriv_gl_cy',
    'deriv_gl_cy_0',
    'sech',
    'sech_np',
    'quasi_sech',
    'quasi_sech_np',
    'sech_cy',
    'sech_cy_0',
    'quasi_sech_cy',
    'quasi_sech_ifft',
    'deriv_quasi_sech',
    'deriv_quasi_sech_reviews',
    'deriv_quasi_sech_fp_reviews',
    'quasi_sech_ifft_fp',
    'deriv_quasi_sech_fp',
    'deriv_quasi_sech_fit_steepness',
    'deriv_quasi_sech_search_steepness',
    'smoothing_zhxyao',
    'EnvelopeFunction',
    'QuasiSechEnvelope',
    'GeneralPeakEnvelope',
    'ArbitraryOrderDerivativeAlgorithm',
    'ArbitraryOrderDerivativeZhxyaoGl',
    'ArbitraryOrderDerivative',
]
# 定义 ============================================================
