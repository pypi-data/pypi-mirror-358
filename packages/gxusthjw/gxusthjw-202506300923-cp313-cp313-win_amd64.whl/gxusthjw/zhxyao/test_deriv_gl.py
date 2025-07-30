#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_deriv_gl.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试deriv_gl.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np

from .deriv_gl import (
    deriv_gl, deriv_gl_0, deriv_gl_1
)


# 定义 ==============================================================
class TestDerivGl(unittest.TestCase):
    """
    测试deriv_gl.py。
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

    def test_consistency(self):
        # 初始化一些测试数据
        test_data = np.array([1.0, 2.0, 4.0, 7.0, 11.0, 12.0, 15.0], dtype=np.float64)
        deriv_orders = [0.0, 0.5, 1.0, 1.5, 2.0, 100, 145, 200, 300]  # 测试不同的导数阶数
        for order in deriv_orders:
            with self.subTest(deriv_order=order):
                result = deriv_gl(test_data, order)
                result_0 = deriv_gl_0(test_data, order)
                result_1 = deriv_gl_1(test_data, order)

                # 使用np.allclose来比较浮点数精度问题
                self.assertTrue(np.allclose(result, result_0),
                                "deriv_gl and deriv_gl_0 results are not close")
                self.assertTrue(np.allclose(result, result_1),
                                "deriv_gl and deriv_gl_1 results are not close")

    # noinspection PyUnresolvedReferences
    def test_consistency_2(self):
        # 设置测试参数
        data_size = 1000  # 数据长度
        # 生成随机测试数据
        test_data = np.random.rand(data_size)
        deriv_orders = [0.0, 0.5, 1.0, 1.5, 2.0, 100, 145, 200, 300]  # 测试不同的导数阶数
        for order in deriv_orders:
            with self.subTest(deriv_order=order):
                result = deriv_gl(test_data, order)
                result_0 = deriv_gl_0(test_data, order)
                result_1 = deriv_gl_1(test_data, order)

                # 使用np.allclose来比较浮点数精度问题
                self.assertTrue(np.allclose(result, result_0),
                                "deriv_gl and deriv_gl_0 results are not close")
                self.assertTrue(np.allclose(result, result_1),
                                "deriv_gl and deriv_gl_1 results are not close")

    def test_consistency_3(self):
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float64)
        y = np.sin(x)
        v = 2
        res = deriv_gl(y, v)
        res_0 = deriv_gl_0(y, v)
        res_1 = deriv_gl_1(y, v)
        matlab_res = np.array([
            0.841470984807897, -0.773644542790111,
            -0.836003860783600, -0.129745084601981,
            0.695800724012585, 0.881630555819423,
            0.256893320453502, -0.604030449013122,
            -0.909611409286218, - 0.378899834749501
        ])
        self.assertTrue(np.allclose(res, matlab_res, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res_0, matlab_res, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res_1, matlab_res, rtol=0, atol=1e-15))

        v = 4
        res = deriv_gl(y, v)
        res_0 = deriv_gl_0(y, v)
        res_1 = deriv_gl_1(y, v)
        matlab_res = np.array([
            0.841470984807897, -2.456586512405904,
            1.552756209604519, 0.768618094175107,
            0.119287032432947, -0.639715976807728,
            -0.810567067172758, -0.236186534100704,
            0.555342809193529, 0.836292534809812
        ])
        self.assertTrue(np.allclose(res, matlab_res, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res_0, matlab_res, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res_1, matlab_res, rtol=0, atol=1e-15))

        v = 8
        res = deriv_gl(y, v)
        res_0 = deriv_gl_0(y, v)
        res_1 = deriv_gl_1(y, v)
        matlab_res = np.array([
            0.841470984807897, -5.822470451637490,
            16.427928168075514, -23.547809757909981,
            17.029168947791149, -5.172766892312850,
            0.942302867559928, -0.540744161812722,
            -0.685162517776352, -0.199645614685219
        ])
        self.assertTrue(np.allclose(res, matlab_res, rtol=0, atol=1e-12))
        self.assertTrue(np.allclose(res_0, matlab_res, rtol=0, atol=1e-12))
        self.assertTrue(np.allclose(res_1, matlab_res, rtol=0, atol=1e-12))


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
