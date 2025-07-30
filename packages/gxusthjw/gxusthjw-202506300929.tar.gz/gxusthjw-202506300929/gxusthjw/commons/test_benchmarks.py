#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_benchmarks.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试benchmarks.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest
from unittest.mock import patch, MagicMock

import numpy as np

from .benchmarks import (
    benchmark,
)


# 定义 ==============================================================
class TestBenchmarks(unittest.TestCase):
    """
    测试benchmarks.py。
    """

    # region
    # --------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        """设置测试环境"""
        self.repeat = 5

        # 创建一个模拟函数
        self.mock_func = MagicMock()

        # 设置默认返回值
        self.mock_func.return_value = None
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

    # noinspection PyUnusedLocal
    @patch('timeit.timeit')
    @patch('numpy.errstate')
    def test_benchmark_normal_execution2(self, mock_errstate, mock_timeit):
        # 模拟 timeit 执行时会实际调用 wrapper 函数
        def side_effect(wrapper_func, number):
            for _ in range(number):
                wrapper_func()
            return 0.5  # 返回总耗时

        mock_timeit.side_effect = side_effect

        result = benchmark(
            self.mock_func,
            self.repeat,
            use_np_errstate=False,
            use_try=False
        )

        self.assertAlmostEqual(result, 0.1)
        self.assertEqual(self.mock_func.call_count, self.repeat)  # 应该成功

    @patch('timeit.timeit')
    @patch('numpy.errstate')
    def test_benchmark_with_use_try_success(self, mock_errstate, mock_timeit):
        """TC03: 不使用 np.errstate 但使用 try-except"""
        mock_timeit.return_value = 0.5

        result = benchmark(
            self.mock_func,
            self.repeat,
            use_np_errstate=False,
            use_try=True
        )

        self.assertAlmostEqual(result, 0.1)
        mock_timeit.assert_called_once()
        mock_errstate.assert_not_called()

    # noinspection PyUnusedLocal
    @patch('timeit.timeit')
    @patch('numpy.errstate')
    def test_benchmark_with_np_errstate_and_use_try(self, mock_errstate, mock_timeit):
        """TC04: 同时使用 np.errstate 和 try-except"""
        mock_timeit.return_value = 0.5

        result = benchmark(
            self.mock_func,
            self.repeat,
            use_np_errstate=True,
            use_try=True
        )

        self.assertAlmostEqual(result, 0.1)
        mock_timeit.assert_called_once()

    @patch('timeit.timeit')
    @patch('numpy.errstate')
    def test_benchmark_with_exception_and_use_try(self, mock_errstate, mock_timeit):
        """TC05: 使用 try-except 且函数抛出异常"""
        mock_timeit.side_effect = Exception("Test exception")

        result = benchmark(
            self.mock_func,
            self.repeat,
            use_np_errstate=False,
            use_try=True
        )

        self.assertEqual(result, float('inf'))
        mock_timeit.assert_called_once()
        mock_errstate.assert_not_called()
        self.assertEqual(self.mock_func.call_count, 0)  # wrapper 应该没有被执行完

    @patch('timeit.timeit')
    @patch('numpy.errstate')
    def test_benchmark_with_exception_without_use_try(self, mock_errstate, mock_timeit):
        """TC06: 不使用 try-except 且函数抛出异常"""
        mock_timeit.side_effect = Exception("Test exception")

        with self.assertRaises(Exception):
            benchmark(
                self.mock_func,
                self.repeat,
                use_np_errstate=False,
                use_try=False
            )

        mock_timeit.assert_called_once()
        mock_errstate.assert_not_called()
        self.assertEqual(self.mock_func.call_count, 0)  # wrapper 应该没有被执行完

    def test_normal_execution(self):
        """T1: 正常执行，无特殊处理"""

        def sample_func():
            pass

        result = benchmark(sample_func, repeat=10)
        self.assertGreater(result, 0)

    def test_use_np_errstate(self):
        """T2: 使用 np.errstate 包裹执行"""

        def div_by_zero():
            return np.array([1]) / np.array([0])

        result = benchmark(div_by_zero, repeat=1, use_np_errstate=True)
        self.assertGreater(result, 0)

    def test_use_try_with_exception(self):
        """T3: 使用 try 并捕获异常"""

        def raises_error():
            raise ValueError("Test error")

        result = benchmark(raises_error, repeat=1, use_try=True)
        self.assertEqual(result, float('inf'))

    def test_no_try_with_exception(self):
        """T4: 不使用 try，预期抛出异常"""

        def raises_error():
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            benchmark(raises_error, repeat=1, use_try=False)

    def test_use_try_and_np_errstate_with_exception(self):
        """T5: 使用 try 和 np.errstate，并抛出异常"""

        def raises_error():
            raise ValueError("Test error")

        result = benchmark(raises_error, repeat=1, use_try=True, use_np_errstate=True)
        self.assertEqual(result, float('inf'))

    def test_np_errstate_handles_warning(self):
        """T6: NumPy 计算函数，验证 np.errstate 处理除零"""

        def div_by_zero():
            return np.array([1]) / np.array([0])

        result = benchmark(div_by_zero, repeat=10, use_np_errstate=True)
        self.assertGreater(result, 0)


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
