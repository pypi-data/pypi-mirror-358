#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        fitting_statistics.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与“拟合统计”相关的类和函数。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Optional

import numpy as np
import numpy.typing as npt
import scipy.stats as stats

from .residuals_analysis import Residuals
from ..commons import NumberSequence

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the classes and functions associated with "fitting statistics".
"""

__all__ = [
    'rsquared',
    'chisqr',
    'chisqr_p',
    'redchi',
    'aic',
    'bic',
    'FittingStatistics'
]

# 定义 ================================================================

# 一个极小的数。
TINY_FLOAT = 1.e-15


# noinspection PyTypeChecker
def rsquared(y_true: NumberSequence,
             y_pred: NumberSequence):
    """
    计算拟合优度（R^2）。

    概念说明：拟合优度 R^2 （又称为决定系数）是衡量回归模型对观测数据拟合程度的一个统计量。
            R^2 的值介于 0 到 1 之间，其中 1 表示模型完美地拟合了数据，
            而 0 表示模型没有提供任何改进，即模型的表现不比使用数据的均值更好。

    算法说明：该算法参考自lmfit包。

    :param y_true: 真实数据（拟合前的数据）。
    :param y_pred:  预测数据（拟合后的数据）。
    :return: 拟合优度（R^2）。
    """
    y_raw = np.asarray(y_true)
    y_fitted = np.asarray(y_pred)
    if y_raw.shape != y_fitted.shape:
        raise ValueError(f"y_true and y_pred must have the same shape,"
                         f"but got y_true.shape = {y_raw.shape}, "
                         f"y_pred.shape = {y_fitted.shape}.")
    # 残差平方和
    ess = np.sum((y_fitted - y_raw) ** 2)
    # 总平方和
    tss = np.sum((y_raw - np.mean(y_raw)) ** 2)
    return 1.0 - ess / max(TINY_FLOAT, tss)


# noinspection PyTypeChecker
def chisqr(y_true: NumberSequence,
           y_pred: NumberSequence):
    """
    计算卡方统计量（chi-square statistic）。

    概念说明：用于度量观测数据的分布与预期或假设分布之间的差异。
            卡方统计量的值越大，表明观测数据与预期分布之间的差异越大。
            为了判断这种差异是否显著，通常会将计算出的卡方统计量与卡方分布表上的临界值进行比较，
            或者计算相应的 p值。

    算法说明：该算法参考自lmfit包。

    :param y_true: 真实数据（拟合前的数据）。
    :param y_pred:  预测数据（拟合后的数据）。
    :return: 卡方统计量（chi-square statistic）。
    """
    y_raw = np.asarray(y_true)
    y_fitted = np.asarray(y_pred)
    if y_raw.shape != y_fitted.shape:
        raise ValueError(f"y_true and y_pred must have the same shape,"
                         f"but got y_true.shape = {y_raw.shape}, "
                         f"y_pred.shape = {y_fitted.shape}.")
    # 残差平方和
    ess = np.sum((y_fitted - y_raw) ** 2)
    return max(ess, 1.0e-250 * y_raw.shape[0])


def chisqr_p(y_true: NumberSequence,
             y_pred: NumberSequence,
             nvars_fitted: int):
    """
    计算卡方检验的p值。

    当len(y_true) <=》nvars_fitted时，不会抛出异常。

    :param y_true: 真实数据（拟合前的数据）。
    :param y_pred:  预测数据（拟合后的数据）。
    :param nvars_fitted: 拟合变量的个数。
    :return:卡方检验的p值。
    """
    return stats.chi2.sf(chisqr(y_true, y_pred),
                         len(y_true) - nvars_fitted)  # type: ignore


# noinspection DuplicatedCode
def redchi(y_true: NumberSequence,
           y_pred: NumberSequence,
           nvars_fitted: int):
    """
    计算简化卡方统计量（reduced chi-square statistic）。

    概念说明：简化卡方统计量接近于1，表示模型很好地拟合了数据。
            如果简化卡方统计量小于1，表示模型可能过度拟合数据。
            如果简化卡方统计量大于1，表示模型可能欠拟合数据或者模型与数据之间存在显著差异。

    算法说明：该算法参考自lmfit包。

    :param y_true: 真实数据（拟合前的数据）。
    :param y_pred:  预测数据（拟合后的数据）。
    :param nvars_fitted: 拟合变量的个数。
    :return:简化卡方统计量（reduced chi-square statistic）。
    """
    y_raw = np.asarray(y_true)
    y_fitted = np.asarray(y_pred)
    y_len = y_raw.shape[0]
    if y_raw.shape != y_fitted.shape:
        raise ValueError(f"y_true and y_pred must have the same shape,"
                         f"but got y_true.shape = {y_raw.shape}, "
                         f"y_pred.shape = {y_fitted.shape}.")
    if nvars_fitted >= y_len:
        raise ValueError(
            "Expected nvars_fitted < {},"
            " but got nvars_fitted = {}.".format(
                y_len, nvars_fitted)
        )
    nfree = y_len - nvars_fitted
    ess = np.sum((y_fitted - y_raw) ** 2)
    return ess / max(1, nfree)


# noinspection DuplicatedCode
def aic(y_true: NumberSequence,
        y_pred: NumberSequence,
        nvars_fitted: int):
    """
    计算赤池信息准则统计量（Akaike information criterion statistic）。

    概念说明：AIC 同时考虑了模型的复杂性和模型对数据的拟合优度。
            较小的 AIC 值表明该模型在保持合理复杂性的前提下提供了较好的拟合。
            在一组候选模型中，选择 AIC 最小的模型作为最优模型。

    算法说明：该算法参考自lmfit包。

    :param y_true: 真实数据（拟合前的数据）。
    :param y_pred:  预测数据（拟合后的数据）。
    :param nvars_fitted: 拟合变量的个数。
    :return: 赤池信息准则统计量（Akaike information criterion statistic）。
    """
    y_raw = np.asarray(y_true)
    y_fitted = np.asarray(y_pred)
    y_len = y_raw.shape[0]
    if y_raw.shape != y_fitted.shape:
        raise ValueError(f"y_true and y_pred must have the same shape,"
                         f"but got y_true.shape = {y_raw.shape}, "
                         f"y_pred.shape = {y_fitted.shape}.")
    if nvars_fitted >= y_len:
        raise ValueError(
            "Expected nvars_fitted < {},"
            " but got nvars_fitted = {}.".format(
                y_len, nvars_fitted)
        )
    ess = np.sum((y_fitted - y_raw) ** 2)
    _chisqr = max(ess, 1.0e-250 * y_raw.shape[0])
    _neg2_log_likelihood = y_len * np.log(_chisqr / y_len)
    return _neg2_log_likelihood + 2 * nvars_fitted


# noinspection DuplicatedCode
def bic(y_true: NumberSequence,
        y_pred: NumberSequence,
        nvars_fitted: int):
    """
    计算贝叶斯信息准则统计量（Bayesian Information Criterion statistic）。

    概念说明：BIC 同时考虑了模型的复杂性和模型对数据的拟合优度。
            较小的 BIC 值表明该模型在保持较低复杂性的前提下提供了较好的拟合。
            在一组候选模型中，选择 BIC 最小的模型作为最优模型。

    算法说明：该算法参考自lmfit包。

    :param y_true: 真实数据（拟合前的数据）。
    :param y_pred: 预测数据（拟合后的数据）。
    :param nvars_fitted: 拟合变量的个数。
    :return: 贝叶斯信息准则统计量（Bayesian Information Criterion statistic）。
    """
    y_raw = np.asarray(y_true)
    y_fitted = np.asarray(y_pred)
    y_len = y_raw.shape[0]
    if y_raw.shape != y_fitted.shape:
        raise ValueError(f"y_true and y_pred must have the same shape,"
                         f"but got y_true.shape = {y_raw.shape}, "
                         f"y_pred.shape = {y_fitted.shape}.")
    if nvars_fitted >= y_len:
        raise ValueError(
            "Expected nvars_fitted < {},"
            " but got nvars_fitted = {}.".format(
                y_len, nvars_fitted)
        )
    ess = np.sum((y_fitted - y_raw) ** 2)
    _chisqr = max(ess, 1.0e-250 * y_raw.shape[0])
    _neg2_log_likelihood = y_len * np.log(_chisqr / y_len)
    return _neg2_log_likelihood + np.log(y_len) * nvars_fitted


# ------------------------------------------------------------------------
class FittingStatistics(Residuals):
    """
    类`FittingStatistics`表征“拟合统计”。
    """

    def __init__(self, y_true: NumberSequence,
                 y_pred: NumberSequence,
                 nvars_fitted: Optional[int] = None,
                 x: Optional[npt.ArrayLike] = None,
                 **kwargs):
        """
        类`FittingStatistics`的初始化方法。

        :param y_true: 真实数据（拟合前的数据）。
        :param y_pred: 预测数据（拟合后的数据）。
        :param nvars_fitted: 拟合变量的个数。
        :param x: 与y数据（因变量）对应的x数据（自变量），可选。
        :param kwargs: 其他可选的关键字参数，将全部转化为对象的属性。
        """
        self.__y_true = np.asarray(y_true)
        self.__len = self.__y_true.shape[0]
        self.__y_pred = np.asarray(y_pred)
        if self.__y_true.shape != self.__y_pred.shape:
            raise ValueError(f"y_true and y_pred must have the same shape,"
                             f"but got y_true.shape = {self.__y_true.shape}, "
                             f"y_pred.shape = {self.__y_pred.shape}.")

        # 残差数据。
        super(FittingStatistics, self).__init__(self.__y_true - self.__y_pred)

        # 残差平方和。
        self.__ess = np.sum(self.residuals ** 2)

        # 离均差（deviation from average）
        self.__devfas = self.__y_true - np.mean(self.__y_true)

        # 离均差平方和。
        self.__tss = np.sum(self.__devfas ** 2)

        # 拟合变量的个数可以不给出，不给出时为None。
        self.__nvars_fitted: Optional[int] = nvars_fitted
        if self.__nvars_fitted is not None:
            if nvars_fitted >= self.__len:  # type: ignore
                raise ValueError(
                    "Expected nvars_fitted < {},"
                    " but got nvars_fitted = {}.".format(
                        self.__len, nvars_fitted)
                )
            # 自由度。
            self.__nfree: Optional[int] = self.__len - self.__nvars_fitted
        else:
            self.__nfree: Optional[int] = None  # type: ignore

        if x is None:
            self.__x = np.arange(self.__len, dtype=np.int64)
        else:
            self.__x = np.asarray(x)
            if self.__x.shape != self.__y_true.shape:
                raise ValueError(f"x and y_true must have the same shape,"
                                 f"but got y_true.shape = {self.__y_true.shape}, "
                                 f"x.shape = {self.__x.shape}.")

        # 可选关键字参数将被转换为对象的属性。
        for key in kwargs.keys():
            if not hasattr(self, key):
                setattr(self, key, kwargs[key])

    @property
    def y_true(self) -> npt.NDArray:
        """
        获取真实数据（拟合前的数据）。

        :return: 真实数据（拟合前的数据）。
        """
        return self.__y_true

    @property
    def y_pred(self) -> npt.NDArray:
        """
        获取预测数据（拟合后的数据）。

        :return: 预测数据（拟合后的数据）。
        """
        return self.__y_pred

    @property
    def x(self) -> npt.NDArray:
        """
        获取与y数据（因变量）对应的x数据（自变量）。

        :return: 与y数据（因变量）对应的x数据（自变量）。
        """
        return self.__x

    @property
    def len(self) -> int:
        """
        获取数据的长度。

        :return: 数据的长度。
        """
        return self.__len

    @property
    def nvars_fitted(self) -> Optional[int]:
        """
        获取拟合变量的数量。

        :return: 拟合变量的数量。
        """
        return self.__nvars_fitted

    @property
    def nfree(self) -> Optional[int]:
        """
        获取自由度。

        :return: 自由度。
        """
        return self.__nfree

    @property
    def ess(self):
        """
        获取拟合残差平方和。

        :return: 拟合残差平方和。
        """
        return self.__ess

    @property
    def devfas(self):
        """
        获取真实数据（拟合前的数据）的离均差。

        :return: 真实数据（拟合前的数据）的离均差。
        """
        return self.__devfas

    @property
    def tss(self):
        """
        获取真实数据（拟合前的数据）的离均差平方和。

        :return: 真实数据（拟合前的数据）的离均差平方和。
        """
        return self.__tss

    # ----------------------------------------------------
    @property
    def chisqr(self):
        """
        获取卡方统计量（chi-square statistic）。

        :return:卡方统计量（chi-square statistic）。
        """
        # noinspection PyTypeChecker
        return max(self.ess, 1.0e-250 * self.len)

    @property
    def redchi(self):
        """
        获取简化卡方统计量（reduced chi-square statistic）。

        :return:简化卡方统计量（reduced chi-square statistic）。
        """
        if self.nfree is not None:
            return self.ess / max(1, self.nfree)
        else:
            return None

    @property
    def likelihood(self):
        """
        获取最大似然估计（Maximum Likelihood Estimate, MLE）。

        :return:最大似然估计（Maximum Likelihood Estimate, MLE）。
        """
        return self.chisqr / self.len

    @property
    def neg2_log_likelihood(self):
        """
        获取 `-2ln(Likelihood)`

        :return: `-2ln(Likelihood)`。
        """
        return self.len * np.log(self.chisqr / self.len)

    @property
    def aic(self):
        """
        获取赤池信息准则统计量（Akaike information criterion statistic）。

        :return:赤池信息准则统计量（Akaike information criterion statistic）。
        """
        if self.nvars_fitted is not None:
            return self.neg2_log_likelihood + 2 * self.nvars_fitted
        else:
            return None

    @property
    def bic(self):
        """
        获取贝叶斯信息准则统计量（Bayesian Information Criterion statistic）。

        :return:贝叶斯信息准则统计量（Bayesian Information Criterion statistic）。
        """
        if self.nvars_fitted is not None:
            return self.neg2_log_likelihood + np.log(self.len) * self.nvars_fitted
        else:
            return None

    @property
    def rsquared(self):
        """
        获取R^2统计量。

        :return:R^2统计量。
        """
        # noinspection PyTypeChecker
        return 1.0 - self.ess / max(TINY_FLOAT, self.tss)

# ==========================================================
