#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_dataframes.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试dataframes.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import array
import unittest
from collections import deque

import pandas as pd
import numpy as np

from .dataframes import (
    update_df
)


# 定义 ==============================================================
class TestDataframe2(unittest.TestCase):
    """
    测试dataframe2.py。
    """

    # region
    # --------------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        self.default_df = pd.DataFrame({'existing_col': [1, 2, 3]})
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

    def test_update_df(self):
        """
        测试update_df()函数。
        """
        df = pd.DataFrame()
        result = update_df(df, 123)
        expected = pd.DataFrame({"item_0": [123]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

        result1 = update_df(df, 123.0)
        expected1 = pd.DataFrame({"item_0": [123.0]})
        pd.testing.assert_frame_equal(result1, expected1, check_dtype=False)

        result2 = update_df(df, np.array([123])[0])
        expected2 = pd.DataFrame({"item_0": [123.0]})
        pd.testing.assert_frame_equal(result2, expected2, check_dtype=False)

        result3 = update_df(df, pd.Series([123])[0])
        expected3 = pd.DataFrame({"item_0": [123.0]})
        pd.testing.assert_frame_equal(result3, expected3, check_dtype=False)

        result4 = update_df(df, np.array([123.0, 254.0]), "test_column")
        expected4 = pd.DataFrame({"test_column": [123.0, 254.0]})
        pd.testing.assert_frame_equal(result4, expected4, check_dtype=False)

        result5 = update_df(df, {1, 2, 3}, "test_column")
        expected5 = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result5, expected5, check_dtype=False)

        result6 = update_df(df, frozenset([1, 2, 3]), "test_column")
        expected6 = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result6, expected6, check_dtype=False)

        # 设置最大长度为3
        d = deque(maxlen=3)
        d.append(1)
        d.append(2)
        d.append(3)
        d.append(4)  # 自动移除最左边的1
        result7 = update_df(df, d, "test_column")
        expected7 = pd.DataFrame({"test_column": [2, 3, 4]})
        pd.testing.assert_frame_equal(result7, expected7, check_dtype=False)

        # 声明一个整数类型的数组，并初始化一些元素
        arr = array.array('i', [1, 2, 3, 4, 5])
        result8 = update_df(df, arr, "test_column")
        expected8 = pd.DataFrame({"test_column": [1, 2, 3, 4, 5]})
        pd.testing.assert_frame_equal(result8, expected8, check_dtype=False)

        result9 = update_df(df, {'a': [1, 2, 3, 4, 5]}, "a")
        expected9 = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
        pd.testing.assert_frame_equal(result9, expected9, check_dtype=False)

        result9 = update_df(df, {'a': 1, 'b': 2}, "f")
        print(result9)

        result10 = update_df(df, np.array(["1", "2"]), "test_column")
        expected10 = pd.DataFrame({"test_column": ["1", "2"]})
        pd.testing.assert_frame_equal(result10, expected10, check_dtype=False)


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
