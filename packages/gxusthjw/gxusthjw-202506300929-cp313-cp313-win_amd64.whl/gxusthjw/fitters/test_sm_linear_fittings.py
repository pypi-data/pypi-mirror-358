#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_sm_linear_fittings.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试sm_linear_fittings.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/18     revise
#       Jiwei Huang        0.0.1         2024/10/22     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

import numpy as np
import statsmodels.api as sm

from .sm_linear_fittings import (
    linear_fitting_sm_rlm,
    linear_fitting_sm_ols,
    linear_fitting_sm
)


# ==================================================================
class TestSmLinearFittings(unittest.TestCase):
    """
    测试sm_linear_fittings.py。
    """

    # --------------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        print("\n\n-----------------------------------------------------")

    def tearDown(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        print("-----------------------------------------------------")

    @classmethod
    def setUpClass(cls):
        """
        Hook method for setting up class fixture before running tests in the class.
        """
        print("\n\n=======================================================")

    @classmethod
    def tearDownClass(cls):
        """
        Hook method for deconstructing the class fixture after running all tests in the class.
        """
        print("=======================================================")

    # --------------------------------------------------------------------

    def test_linear_fitting_sm_rlm(self):
        # 示例数据
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 3, 5, 7, 11])

        # 执行线性拟合
        fitting_result = linear_fitting_sm_rlm(y, x)
        print(type(fitting_result))  # RLMResultsWrapper

        # 输出拟合结果
        print("拟合结果:")
        print(f"参数估计: {fitting_result.params}")
        print(f"标准误差: {fitting_result.bse}")
        print(f"残差自由度 (df_resid): {fitting_result.df_resid}")
        print(f"尺度参数 (Scale): {fitting_result.scale}")

        # 预测新数据点
        x_new = np.array([6, 7, 8])
        x_new_with_const = sm.add_constant(x_new)
        y_pred = fitting_result.predict(x_new_with_const)

        print("\n预测结果:")
        print(f"新数据点: {x_new}")
        print(f"预测值: {y_pred}")

    def test_linear_fitting_sm_ols(self):
        # 示例数据
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 3, 5, 7, 11])

        # 执行线性拟合
        fitting_result = linear_fitting_sm_ols(y, x)
        print(type(fitting_result))  # RegressionResultsWrapper

        # 输出拟合结果
        print("拟合结果:")
        print(f"参数估计: {fitting_result.params}")
        print(f"标准误差: {fitting_result.bse}")
        print(f"R-squared: {fitting_result.rsquared}")
        print(f"调整后的 R-squared: {fitting_result.rsquared_adj}")
        print(f"残差标准误 (MSE): {fitting_result.mse_resid}")
        print(f"F 统计量: {fitting_result.fvalue}")
        print(f"p 值: {fitting_result.f_pvalue}")

        # 预测新数据点
        x_new = np.array([6, 7, 8])
        x_new_with_const = sm.add_constant(x_new)
        y_pred = fitting_result.predict(x_new_with_const)

        print("\n预测结果:")
        print(f"新数据点: {x_new}")
        print(f"预测值: {y_pred}")

    def test_linear_fitting_sm(self):
        # 示例数据
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 3, 5, 7, 11])

        # 使用 OLS 方法进行线性拟合
        fitting_result_ols = linear_fitting_sm(y, x, method="ols")

        # 输出 OLS 拟合结果
        print("OLS 拟合结果:")
        print(f"参数估计: {fitting_result_ols.params}")
        print(f"标准误差: {fitting_result_ols.bse}")
        print(f"R-squared: {fitting_result_ols.rsquared}")
        print(f"调整后的 R-squared: {fitting_result_ols.rsquared_adj}")
        print(f"残差标准误 (MSE): {fitting_result_ols.mse_resid}")
        print(f"F 统计量: {fitting_result_ols.fvalue}")
        print(f"p 值: {fitting_result_ols.f_pvalue}")

        # 预测新数据点（OLS）
        x_new = np.array([6, 7, 8])
        x_new_with_const = sm.add_constant(x_new)
        y_pred_ols = fitting_result_ols.predict(x_new_with_const)

        print("\nOLS 预测结果:")
        print(f"新数据点: {x_new}")
        print(f"预测值: {y_pred_ols}")

        # 使用 RLM 方法进行线性拟合
        fitting_result_rlm = linear_fitting_sm(y, x, method="rlm")

        # 输出 RLM 拟合结果
        print("\nRLM 拟合结果:")
        print(f"参数估计: {fitting_result_rlm.params}")
        print(f"标准误差: {fitting_result_rlm.bse}")
        print(f"残差自由度 (df_resid): {fitting_result_rlm.df_resid}")
        print(f"尺度参数 (Scale): {fitting_result_rlm.scale}")

        # 预测新数据点（RLM）
        y_pred_rlm = fitting_result_rlm.predict(x_new_with_const)

        print("\nRLM 预测结果:")
        print(f"新数据点: {x_new}")
        print(f"预测值: {y_pred_rlm}")


if __name__ == '__main__':
    unittest.main()
