#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_data_analyzer.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_analyzer.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

from .data_analyzer import DataAnalyzer


# 定义 ==============================================================
class TestDataAnalyzer(unittest.TestCase):
    """
    测试data_analyzer.py。
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

    def test_init(self):
        """
        测试DataAnalyzer的初始化方法。
        """
        da = DataAnalyzer()
        print(da.data_analyzer_name)
        da.data_logger.print()

        da = DataAnalyzer(1, (1,), [1, 2], {'a': 1, 'b': 2})
        print(da.data_analyzer_name)
        da.data_logger.print()

        da = DataAnalyzer(1, (1,), [1, 2], {'a': 1, 'b': 2},
                          data_analyzer_name="data_analyzer_name",
                          data_logger_name="data_logger_name")
        print(da.data_analyzer_name)
        da.data_logger.print()

        da = DataAnalyzer(1, (1,), [1, 2], {'a': 1, 'b': 2},
                          data_analyzer_name="data_analyzer_name",
                          data_logger_name="data_logger_name",
                          c=1, b=3, d=4)

        print(da.data_analyzer_name)
        da.data_logger.print()

    def test_init2(self):
        """
        再次测试DataAnalyzer的初始化方法。
        """
        print("----------------------------------------")
        da1 = DataAnalyzer()
        self.assertEqual(da1.data_analyzer_name, "DataAnalyzer")
        self.assertEqual(da1.data_logger.datalogger_owner, da1)
        da1.data_logger.print()

        da2 = DataAnalyzer(data_analyzer_name=None)
        self.assertEqual(da2.data_analyzer_name, "DataAnalyzer")
        self.assertEqual(da2.data_logger.datalogger_owner, da2)
        da2.data_logger.print()

        da3 = DataAnalyzer(data_analyzer_name="")
        self.assertEqual(da3.data_analyzer_name, "DataAnalyzer")
        self.assertEqual(da3.data_logger.datalogger_owner, da3)
        da3.data_logger.print()

        da4 = DataAnalyzer(data_analyzer_name="   ")
        self.assertEqual(da4.data_analyzer_name, "DataAnalyzer")
        self.assertEqual(da4.data_logger.datalogger_owner, da4)
        da4.data_logger.print()

        da5 = DataAnalyzer(data_analyzer_name="da5")
        self.assertEqual(da5.data_analyzer_name, "da5")
        self.assertEqual(da5.data_logger.datalogger_owner, da5)
        da5.data_logger.print()
        print("----------------------------------------")



if __name__ == '__main__':
    unittest.main()
