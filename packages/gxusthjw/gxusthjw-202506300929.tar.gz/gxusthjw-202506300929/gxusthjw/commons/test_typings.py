#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_typings.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试typings.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
from pprint import pprint

import numpy as np
import pandas as pd

from .typings import (
    is_number,
    is_number_sequence,
    is_numbers,
    is_numeric,
    is_number_ndarray,
    is_number_1darray,
    to_number_1darray,
)


# ==================================================================
class TestTypings(unittest.TestCase):
    """
    测试typings.py。
    """

    # region
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
    # endregion

    # noinspection PyTypeChecker
    def test_is_number(self):
        self.assertTrue(is_number(1))
        self.assertTrue(is_number(1.0))
        self.assertFalse(is_number('1'))
        self.assertFalse(is_number("1"))
        self.assertFalse(is_number(object))
        self.assertFalse(is_number([1, 2]))

        a = np.array([1, 2, 3])
        b = pd.Series([1.0, 2.0, 3.0])
        self.assertTrue(is_number(a[0]))
        self.assertTrue(is_number(a[1]))
        self.assertTrue(is_number(a[2]))
        print(type(a[0]))
        print(type(a[1]))
        print(type(a[2]))
        self.assertTrue(is_number(b[0]))
        self.assertTrue(is_number(b[1]))
        self.assertTrue(is_number(b[2]))
        print(type(b[0]))
        print(type(b[1]))
        print(type(b[2]))

        for ai in a:
            self.assertTrue(is_number(ai))

        for bi in b:
            self.assertTrue(is_number(bi))

    def test_is_number_seq(self):
        test_data = [
            [1, 2.5, 3],  # 列表，符合条件
            (4, 5.6, 7),  # 元组，符合条件
            np.array([8, 9.0]),  # NumPy 数组，符合条件
            [1, 'two', 3],  # 包含非数字的列表
            ('four', 5.0),  # 包含非数字的元组
            np.array(['six', 7]),  # 包含非数字的 NumPy 数组
            "not a number",  # 字符串，不符合条件
            42,  # 单个数字，但不是序列或数组
            {1, 2, 3, 4, 5},
            pd.Series([1, 2, 3, 4, 5])
        ]

        for td in test_data:
            print(f"Data: {td} is NumberSequence? {is_number_sequence(td)}")

    def test_is_numbers(self):
        test_data = [
            [1, 2.5, 3],  # 列表，符合条件
            (4, 5.6, 7),  # 元组，符合条件
            np.array([8, 9.0]),  # NumPy 数组，符合条件
            {1, 2.5, 3},  # 集合，符合条件
            range(5),  # range 对象，符合条件
            [1, 'two', 3],  # 包含非数字的列表
            ('four', 5.0),  # 包含非数字的元组
            np.array(['six', 7]),  # 包含非数字的 NumPy 数组
            "not a number",  # 字符串，不符合条件
            42,  # 单个数字，但不是可迭代对象
            {1, 2, 3, 4, 5}
        ]

        for td in test_data:
            print(f"Data: {td} is Numbers? {is_numbers(td)}")

    def test_is_numeric(self):
        test_data = [
            1,  # 整数，符合条件
            2.5,  # 浮点数，符合条件
            np.array([8, 9.0]),  # NumPy 数组，符合条件
            [1, 2, 3],  # 列表，不符合条件
            'not a number',  # 字符串，不符合条件
            42.0 + 3j,  # 复数，不符合条件
            (4, 5.6),  # 元组，不符合条件
            {'key': 42},  # 字典，不符合条件
        ]

        for td in test_data:
            print(f"Data: {td} is Numeric? {is_numeric(td)}")

    def test_is_number_ndarray_NumpyArrayWithNumericType_ReturnsTrue(self):
        data = np.array([1, 2, 3], dtype=np.int32)
        self.assertTrue(is_number_ndarray(data))

    # noinspection PyTypeChecker
    def test_is_number_ndarray_NumpyArrayWithNonNumericType_ReturnsFalse(self):
        data = np.array(['a', 'b', 'c'], dtype=np.object_)
        self.assertFalse(is_number_ndarray(data))

    # noinspection PyTypeChecker
    def test_is_number_ndarray_NonNumpyArray_ReturnsFalse(self):
        data = [1, 2, 3]
        self.assertFalse(is_number_ndarray(data))

    def test_is_number_ndarray_EmptyNumpyArray_ReturnsTrue(self):
        data = np.array([], dtype=np.float64)
        self.assertTrue(is_number_ndarray(data))

    # noinspection PyTypeChecker
    def test_is_number_ndarray_NumpyArrayWithMixedTypes_ReturnsFalse(self):
        data = np.array([1, 'a', 3.0], dtype=np.object_)
        self.assertFalse(is_number_ndarray(data))

    def test_is_number_ndarray(self):
        test_data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertTrue(is_number_ndarray(test_data))

    def test_is_number_1darray(self):
        test_data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertFalse(is_number_1darray(test_data))

    def test_to_number_1darray(self):
        a = [[1, 2, 3, 4]]
        self.assertRaises(ValueError, to_number_1darray, a)
        b = [1, 2, 3, 4]
        pprint(to_number_1darray(b))
        self.assertRaises(ValueError, to_number_1darray, {1, 2, 3, 4})


if __name__ == '__main__':
    unittest.main()
