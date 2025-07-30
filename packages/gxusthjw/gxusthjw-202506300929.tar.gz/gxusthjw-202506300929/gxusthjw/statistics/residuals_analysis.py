#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        residuals_analysis.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“残差”相关的类和函数。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# ------------------------------------------------------------------
# 导包 ============================================================
import numpy as np
import numpy.typing as npt

from statsmodels.tsa.stattools import acf
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox

from ..commons import NumberSequence

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the classes and functions associated with "residuals".
"""

__all__ = [
    'Residuals',
]


# 定义 ============================================================

class Residuals(object):
    """
    类`Residuals`表征“残差”。
    """

    def __init__(self, residuals: NumberSequence):
        """
        类`Residuals`的初始化方法。

        :param residuals: 残差数据。
        """
        self.__residuals = np.asarray(residuals)
        self.__residuals_len = self.__residuals.shape[0]

    @property
    def residuals(self) -> npt.NDArray:
        """
        返回残差数据。

        :return: 残差数据。
        """
        return self.__residuals

    @property
    def residuals_len(self) -> int:
        """
        返回残差数据的长度。

        :return: 残差数据的长度。
        """
        return self.__residuals_len

    def acf(self, **kwargs):
        """
        返回残差的自相关函数（Auto-correlation Function, ACF）。

        :param kwargs: 计算ACF所需的参数。
        :return: ACF值。
        """
        adjusted = kwargs.pop('adjusted', False)
        nlags = kwargs.pop('nlags', None)
        qstat = kwargs.pop('qstat', False)
        fft = kwargs.pop('fft', True)
        alpha = kwargs.pop('alpha', None)
        bartlett_confint = kwargs.pop('bartlett_confint', True)
        missing = kwargs.pop('missing', "none")
        return acf(self.residuals, adjusted=adjusted, nlags=nlags,
                   qstat=qstat, fft=fft, alpha=alpha,
                   bartlett_confint=bartlett_confint,
                   missing=missing)

    def plot_acf(self, **kwargs):
        """
        绘制自相关函数。

        :param kwargs: 绘制自相关函数所需参数。
        :return: Figure
        """
        ax = kwargs.pop('ax', None)
        lags = kwargs.pop('lags', None)
        alpha = kwargs.pop('alpha', 0.05)
        use_vlines = kwargs.pop('use_vlines', True)
        adjusted = kwargs.pop('adjusted', False)
        fft = kwargs.pop('fft', False)
        missing = kwargs.pop('missing', "none")
        title = kwargs.pop('title', "Autocorrelation"),
        zero = kwargs.pop('zero', True)
        auto_ylims = kwargs.pop('auto_ylims', False)
        bartlett_confint = kwargs.pop('bartlett_confint', True)
        vlines_kwargs = kwargs.pop('vlines_kwargs', None)
        return plot_acf(self.residuals, ax=ax, lags=lags, alpha=alpha,
                        use_vlines=use_vlines, adjusted=adjusted, fft=fft,
                        missing=missing, title=title, zero=zero,
                        auto_ylims=auto_ylims, bartlett_confint=bartlett_confint,
                        vlines_kwargs=vlines_kwargs, **kwargs)

    def acorr_ljungbox(self, **kwargs):
        """
        残差自相关的Ljung-Box检验.

        :param kwargs: 所需关键字参数。
        :return: pd.DataFrame
        """
        lags = kwargs.pop('lags', None)
        boxpierce = kwargs.pop('boxpierce', False)
        model_df = kwargs.pop('model_df', 0)
        period = kwargs.pop('period', None),
        return_df = kwargs.pop('return_df', True)
        auto_lag = kwargs.pop('auto_lag', False)
        return acorr_ljungbox(self.residuals, lags=lags, boxpierce=boxpierce,
                              model_df=model_df, period=period,
                              return_df=return_df, auto_lag=auto_lag)
