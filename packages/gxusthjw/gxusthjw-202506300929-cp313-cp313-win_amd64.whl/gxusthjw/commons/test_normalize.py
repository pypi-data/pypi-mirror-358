#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_normalize.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试normalize.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/31     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np
from .normalizer import normalize
# 定义 ==============================================================
class TestNormalize(unittest.TestCase):
    """
    测试normalize.py。
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

    # --------------------------------------------------------------
    # 测试用例：正常情况
    # --------------------------------------------------------------

    def test_normalize_normal_case(self):
        """
        正常情况：输入数据为 [1, 2, 3, 4, 5]，new_range=(0, 1)
        预期结果：[0.0, 0.25, 0.5, 0.75, 1.0]
        """
        data = [1, 2, 3, 4, 5]
        expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        result = normalize(data)
        self.assertTrue(np.allclose(result, expected))

    # --------------------------------------------------------------
    # 测试用例：自定义范围
    # --------------------------------------------------------------

    def test_normalize_custom_range(self):
        """
        自定义范围：输入数据为 [10, 20, 30]，new_range=(1, 3)
        预期结果：[1.0, 2.0, 3.0]
        """
        data = [10, 20, 30]
        new_range = (1, 3)
        expected = np.array([1.0, 2.0, 3.0])
        result = normalize(data, new_range)
        self.assertTrue(np.allclose(result, expected))

    # --------------------------------------------------------------
    # 测试用例：new_range 上下限相等
    # --------------------------------------------------------------

    def test_normalize_upper_equal_lower(self):
        """
        new_range 上下限相等，应抛出 ValueError
        """
        with self.assertRaises(ValueError):
            normalize([1, 2, 3], new_range=(2, 2))

    # --------------------------------------------------------------
    # 测试用例：new_range 上限小于下限
    # --------------------------------------------------------------

    def test_normalize_upper_less_than_lower(self):
        """
        new_range 上限小于下限，应抛出 ValueError
        """
        with self.assertRaises(ValueError):
            normalize([1, 2, 3], new_range=(3, 1))

    # --------------------------------------------------------------
    # 测试用例：所有数据相同，导致除以零错误
    # --------------------------------------------------------------

    def test_normalize_constant_data(self):
        """
        所有数据相同，应抛出 ZeroDivisionError
        """
        normalize([5, 5, 5])

    # --------------------------------------------------------------
    # 测试用例：多维数组输入
    # --------------------------------------------------------------

    def test_normalize_2d_array(self):
        """
        输入为二维数组 [[1, 2], [3, 4]]，new_range=(0, 1)
        预期结果：[[0.0, 0.3333...], [0.6666..., 1.0]]
        """
        data = [[1, 2], [3, 4]]
        expected = np.array([[0.0, 1/3], [2/3, 1.0]])
        result = normalize(data, new_range=(0, 1))
        self.assertTrue(np.allclose(result, expected))

    # --------------------------------------------------------------
    # 测试用例：无效数据类型（如字符串）
    # --------------------------------------------------------------

    # noinspection PyTypeChecker
    def test_normalize_invalid_data_type(self):
        """
        输入为非数值类型 ['a', 'b']，应抛出 TypeError 或 ValueError
        """
        with self.assertRaises((TypeError, ValueError)):
            normalize(['a', 'b'])

    # --------------------------------------------------------------
    def test_normalize(self):
        data = np.array([1,2,3,4,5])
        # d1 = normalize(data,norm="l1")
        # d2 = normalize(data, norm="l2")
        # d3 = normalize(data, norm="max")
        from .normalizer import (
            normalize as norm,
            z_score,
            decimal_scaling
        )
        da1 = norm(data)
        print(da1)
        da2 = z_score(data)
        print(da2)
        da3 = decimal_scaling(data)
        print(da3)

# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
