#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        sm_linear_fittings.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      基于`statsmodels`包提供的线性拟合方法，
#                   对指定的数据（y，x）执行拟合。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/18     revise
#       Jiwei Huang        0.0.1         2024/10/22     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Any

import numpy as np
import statsmodels.api as sm

from ..commons import NumberSequence

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the functions to perform linear fitting on the specified data
 using the linear regression method provided by the statsmodels library.
"""

__all__ = [
    "linear_fitting_sm_rlm",
    "linear_fitting_sm_ols",
    "linear_fitting_sm",
]


# 定义 ==============================================================
# noinspection PyTypeChecker
def linear_fitting_sm_rlm(y: NumberSequence, x: NumberSequence) -> Any:
    """
    基于statsmodels提供的线性拟合方法（RLM）对指定的数据（y，x）执行拟合。

    要求：

        1. y为一维数值数组。

        2. x为一维数值数组。

        3. 要求y的长度与x的长度相同，但本方法不做长度相等性检查。

        4. 实际的返回值类型：`statsmodels.robust.robust_linear_model.RLMResultsWrapper`

    :param y: 因变量。
    :param x: 自变量。
    :return: 拟合结果。
    """
    x_var = np.column_stack((x,))
    x_var = sm.add_constant(x_var)
    fitting_result = sm.RLM(y, x_var).fit()
    return fitting_result


# noinspection PyTypeChecker
def linear_fitting_sm_ols(y: NumberSequence, x: NumberSequence) -> Any:
    """
    基于statsmodels提供的线性拟合方法（OLS）对指定的数据（y，x）执行拟合。

    要求：

        1. y为一维数值数组。

        2. x为一维数值数组。

        3. 要求y的长度与x的长度相同，但本方法不做长度相等性检查。

        4. 实际返回值类型：`statsmodels.regression.linear_model.RegressionResultsWrapper`

    :param y: 因变量。
    :param x: 自变量。
    :return: 拟合结果。
    """
    x_var = np.column_stack((x,))
    x_var = sm.add_constant(x_var)
    fitting_res = sm.OLS(y, x_var).fit()
    return fitting_res


def linear_fitting_sm(
    y: NumberSequence, x: NumberSequence, method: str = "ols"
) -> Any:
    """
    基于statsmodels提供的线性拟合方法（OLS或RLM）对指定的数据（y，x）执行拟合。

    要求：

        1. y为一维数值数组。

        2. x为一维数值数组。

        3. 要求y的长度与x的长度相同，但本方法不做长度相等性检查。

    :param y: 因变量。
    :param x: 自变量。
    :param method: 拟合方法，必须为 'ols' 或 ‘rlm’，
                   默认值：'ols'，忽略大小写。
    :return: 拟合结果。
    """
    method = method.strip().lower()
    if method == "ols":
        return linear_fitting_sm_ols(y, x)
    elif method.lower() == "rlm":
        return linear_fitting_sm_rlm(y, x)
    else:
        raise ValueError("method must be 'ols' or 'rlm'.")


# ============================================================
