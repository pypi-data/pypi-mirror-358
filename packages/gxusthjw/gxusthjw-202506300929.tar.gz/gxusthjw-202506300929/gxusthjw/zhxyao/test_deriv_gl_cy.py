#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_deriv_gl_cy.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试deriv_gl_cy.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np
from .deriv_gl import deriv_gl
from .cython import (
    deriv_gl_cy, deriv_gl_cy_0
)


# 定义 ==============================================================
class TestDerivGlCy(unittest.TestCase):
    """
    测试deriv_gl_cy.py。
    """

    # region
    # --------------------------------------------------------------
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

    # --------------------------------------------------------------
    # endregion

    def test_sine_function_half_order(self):
        """测试正弦函数的0.5阶导数"""
        x = np.linspace(0, 4 * np.pi, 100)
        y = np.sin(x)
        self._run_test(y, 0.5)

    def test_sine_function_first_order(self):
        """测试正弦函数的一阶导数（应为余弦）"""
        x = np.linspace(0, 4 * np.pi, 100)
        y = np.sin(x)
        self._run_test(y, 1.0)

    def test_linear_function_first_order(self):
        """测试线性函数的一阶导数（应为常数）"""
        y = np.linspace(0, 10, 100)
        self._run_test(y, 1.0)

    def test_random_data_fractional_order(self):
        """测试随机数据的分数阶导数"""
        y = np.random.rand(100)
        self._run_test(y, 0.3)

    def test_integer_second_order(self):
        """测试单调递增序列的二阶导数"""
        y = np.arange(100, dtype=np.float64)
        self._run_test(y, 2.0)

    def test_empty_input(self):
        self.assertTrue(np.allclose(deriv_gl(np.array([]), 1.0), np.array([])))
        self.assertTrue(np.allclose(deriv_gl_cy(np.array([]), 1.0), np.array([])))
        self.assertTrue(np.allclose(deriv_gl_cy_0(np.array([]), 1.0), np.array([])))

    def _run_test(self, data_y, deriv_order):
        res = deriv_gl(data_y, deriv_order)
        res_cy = deriv_gl_cy(data_y, deriv_order)
        res_cy_0 = deriv_gl_cy_0(data_y, deriv_order)

        # 检查形状是否一致
        self.assertEqual(res.shape, res_cy.shape,
                         f"The output shapes are inconsistent.: {res.shape} vs {res_cy.shape}")
        # 检查形状是否一致
        self.assertEqual(res.shape, res_cy_0.shape,
                         f"The output shapes are inconsistent.: {res.shape} vs {res_cy_0.shape}")

        # 检查数值是否接近
        max_diff = np.max(np.abs(res - res_cy))
        # 检查数值是否接近
        max_diff_0 = np.max(np.abs(res - res_cy_0))

        print(f"deriv_order={deriv_order}, Maximum difference value: {max_diff:.2e}")
        print(f"deriv_order={deriv_order}, Maximum difference value: {max_diff_0:.2e}")

        self.assertTrue(np.allclose(res, res_cy, atol=1e-6),
                        f"The results are inconsistent，deriv_order={deriv_order}")

        self.assertTrue(np.allclose(res, res_cy_0, atol=1e-6),
                        f"The results are inconsistent，deriv_order={deriv_order}")

    def test_deriv_gl(self):
        # 构造一个测试输入数据
        data_y = np.sin(np.linspace(0, 4 * np.pi, 100))
        deriv_order = 0.5  # 分数阶导数测试

        # 计算两个版本的结果
        res = deriv_gl(data_y, deriv_order)
        res_cy = deriv_gl_cy(data_y, deriv_order)
        res_cy_0 = deriv_gl_cy_0(data_y, deriv_order)

        # 比较结果是否一致（考虑浮点误差）
        assert np.allclose(res, res_cy, atol=1e-6), "结果不一致，请检查算法差异！"
        assert np.allclose(res, res_cy_0, atol=1e-6), "结果不一致，请检查算法差异！"
        print("✅ 测试通过：新旧版本计算结果一致。")

        deriv_order = 0  # 分数阶导数测试

        # 计算两个版本的结果
        res = deriv_gl(data_y, deriv_order)
        res_cy = deriv_gl_cy(data_y, deriv_order)
        res_cy_0 = deriv_gl_cy_0(data_y, deriv_order)
        # 比较结果是否一致（考虑浮点误差）
        assert np.allclose(res, res_cy, atol=1e-6), "结果不一致，请检查算法差异！"
        assert np.allclose(res, res_cy_0, atol=1e-6), "结果不一致，请检查算法差异！"
        print("✅ 测试通过：新旧版本计算结果一致。")

        deriv_order = 1  # 分数阶导数测试

        # 计算两个版本的结果
        res = deriv_gl(data_y, deriv_order)
        res_cy = deriv_gl_cy(data_y, deriv_order)
        res_cy_0 = deriv_gl_cy_0(data_y, deriv_order)

        # 比较结果是否一致（考虑浮点误差）
        assert np.allclose(res, res_cy, atol=1e-6), "结果不一致，请检查算法差异！"
        assert np.allclose(res, res_cy_0, atol=1e-6), "结果不一致，请检查算法差异！"
        print("✅ 测试通过：新旧版本计算结果一致。")

        deriv_order = 100  # 分数阶导数测试

        # 计算两个版本的结果
        res = deriv_gl(data_y, deriv_order)
        res_cy = deriv_gl_cy(data_y, deriv_order)
        res_cy_0 = deriv_gl_cy_0(data_y, deriv_order)

        # 比较结果是否一致（考虑浮点误差）
        assert np.allclose(res, res_cy_0, atol=1e-6), "结果不一致，请检查算法差异！"
        # 注意：结果不一致。
        self.assertFalse(np.allclose(res, res_cy, atol=1e-6))
        print("✅ 测试通过：新旧版本计算结果一致。")

        deriv_order = 159  # 分数阶导数测试

        # 计算两个版本的结果
        res = deriv_gl(data_y, deriv_order)
        res_cy = deriv_gl_cy(data_y, deriv_order)
        res_cy_0 = deriv_gl_cy_0(data_y, deriv_order)

        # 比较结果是否一致（考虑浮点误差）
        assert np.allclose(res, res_cy, atol=1e-6), "结果不一致，请检查算法差异！"
        assert np.allclose(res, res_cy_0, atol=1e-6), "结果不一致，请检查算法差异！"
        print("✅ 测试通过：新旧版本计算结果一致。")


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
