#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_data_logger.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_logger.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
from unittest.mock import Mock
import numpy as np
import pandas as pd

from .data_logger import DataLogger


# 定义 ==============================================================
class TestDataLogger(unittest.TestCase):
    """
    测试data_logger.py。
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

    # noinspection PyUnresolvedReferences
    def test_init(self):
        dl = DataLogger()
        self.assertEqual(dl._DataLogger__datalogger_name, "DataLogger_DataLogger")
        self.assertEqual(dl.datalogger_name, "DataLogger_DataLogger")
        self.assertFalse(dl.is_empty)
        self.assertEqual(dl.shape, (1, 2))
        dl.print()

        # 测试使用自定义名称初始化
        custom_name = "CustomName"
        dl2 = DataLogger(datalogger_name=custom_name)
        self.assertEqual(dl2._DataLogger__datalogger_name, custom_name)
        self.assertEqual(dl2.datalogger_name, custom_name)
        self.assertFalse(dl2.is_empty)
        self.assertEqual(dl2.shape, (1, 2))
        dl2.print()

        # 测试使用owner初始化
        owner = Mock()
        owner.__class__.__name__ = "MockOwner"
        dl3 = DataLogger(datalogger_owner=owner)
        self.assertEqual(dl3._DataLogger__datalogger_owner, owner)
        self.assertEqual(dl3.datalogger_owner, owner)
        self.assertEqual(dl3._DataLogger__datalogger_name, "MockOwner_DataLogger")
        self.assertEqual(dl3.datalogger_name, "MockOwner_DataLogger")
        self.assertFalse(dl3.is_empty)
        self.assertEqual(dl3.shape, (1, 2))
        dl3.print()

        # 测试使用owner和自定义名称初始化
        owner = Mock()
        owner.__class__.__name__ = "MockOwner"
        custom_name = "CustomName"
        dl4 = DataLogger(datalogger_owner=owner, datalogger_name=custom_name)
        self.assertEqual(dl4._DataLogger__datalogger_owner, owner)
        self.assertEqual(dl4.datalogger_owner, owner)
        self.assertEqual(dl4._DataLogger__datalogger_name, custom_name)
        self.assertEqual(dl4.datalogger_name, custom_name)
        self.assertFalse(dl4.is_empty)
        self.assertEqual(dl4.shape, (1, 2))
        dl4.print()

        # 测试pandas.DataFrame是否正确初始化
        dl5 = DataLogger()
        self.assertIsInstance(dl5._DataTable__df, pd.DataFrame)
        self.assertIsInstance(dl5.to_dataframe(), pd.DataFrame)
        self.assertFalse(dl5._DataTable__df.empty)
        self.assertFalse(dl5.is_empty)
        self.assertEqual(dl5.shape, (1, 2))
        dl5.print()

    # noinspection PyUnresolvedReferences
    def test_init_OwnerNone_NameNone(self):
        logger = DataLogger()
        self.assertIs(logger._DataLogger__datalogger_owner, logger)
        self.assertEqual(logger._DataLogger__datalogger_name, "DataLogger_DataLogger")
        self.assertTrue(isinstance(logger._DataTable__df, pd.DataFrame))
        self.assertTrue("DataLoggerName" in logger._DataTable__df.columns)
        self.assertEqual(logger._DataTable__df["DataLoggerName"][0], "DataLogger_DataLogger")

    # noinspection PyUnresolvedReferences
    def test_init_OwnerProvided_NameNone(self):
        class DummyOwner:
            pass

        owner = DummyOwner()
        logger = DataLogger(datalogger_owner=owner)
        self.assertIs(logger._DataLogger__datalogger_owner, owner)
        self.assertEqual(logger._DataLogger__datalogger_name, "DummyOwner_DataLogger")
        self.assertTrue(isinstance(logger._DataTable__df, pd.DataFrame))
        self.assertTrue("DataLoggerName" in logger._DataTable__df.columns)
        self.assertEqual(logger._DataTable__df["DataLoggerName"][0], "DummyOwner_DataLogger")

    # noinspection PyUnresolvedReferences
    def test_init_OwnerNone_NameProvided(self):
        logger = DataLogger(datalogger_name="CustomLogger")
        self.assertIs(logger._DataLogger__datalogger_owner, logger)
        self.assertEqual(logger._DataLogger__datalogger_name, "CustomLogger")
        self.assertTrue(isinstance(logger._DataTable__df, pd.DataFrame))
        self.assertTrue("DataLoggerName" in logger._DataTable__df.columns)
        self.assertEqual(logger._DataTable__df["DataLoggerName"][0], "CustomLogger")

    # noinspection PyUnresolvedReferences
    def test_init_OwnerProvided_NameProvided(self):
        class DummyOwner:
            pass

        owner = DummyOwner()
        logger = DataLogger(datalogger_owner=owner, datalogger_name="CustomLogger")
        self.assertIs(logger._DataLogger__datalogger_owner, owner)
        self.assertEqual(logger._DataLogger__datalogger_name, "CustomLogger")
        self.assertTrue(isinstance(logger._DataTable__df, pd.DataFrame))
        self.assertTrue("DataLoggerName" in logger._DataTable__df.columns)
        self.assertEqual(logger._DataTable__df["DataLoggerName"][0], "CustomLogger")

    def test_update_item(self):
        dl = DataLogger()
        dl.log(np.array([1, 2, 3]))
        self.assertEqual(dl.shape, (3, 3))
        dl.print()
        dl.log(1)
        dl.log(2.0)
        dl.log('a')
        dl.log((True, False))
        dl.log((3, None))
        dl.print()
        dl.log((1, 2, 3, 4, 5), name='test')
        dl.log('item_1', name='item_1')
        dl.print()

    def test_update_item2(self):
        dl = DataLogger(name="A DataLogger")
        dl.log(np.array([1, 2, 3]))
        dl.log((1, 2, 3))
        dl.log([1, 2, 3])
        dl.log(pd.Series([1, 2, 3]))
        dl.log(1, name='test')
        dl.print()

    def test_to(self):
        dl = DataLogger()
        dl.log(np.array([1, 2, 3]))
        dl.log(1)
        dl.log(2.0)
        dl.log('a')
        dl.log((True, False))
        dl.log((3, None))
        dl.log((1, 2, 3, 4, 5), name='test')
        dl.print()
        dl.logs(1, 2, 3, [1, 2, 3], np.array([1]), (True, False), ('a',), 'b', "1,2")
        dl.print({'display.max_columns': None, 'display.max_rows': None,
                  'display.max_colwidth': None})

    def test_create_df_from_item(self):
        # noinspection PyProtectedMember
        from .dataframes import create_df_from_item
        print(create_df_from_item(1, 'a'))
        print(create_df_from_item(2.0, 'a'))
        print(create_df_from_item("123", 'a'))
        print(create_df_from_item((1, 2, "123"), 'a'))
        print(create_df_from_item([1, 2, "123"], 'a'))
        print(create_df_from_item({1, 2, "123"}, 'a'))
        print(create_df_from_item(np.array([1, 2, 3]), 'a'))
        print(create_df_from_item(pd.Series([1, 2, 3]), 'a'))
        import array
        arr = array.array('i', [1, 2, 3, 4, 5])
        print(arr)
        print(create_df_from_item(arr, 'a'))
        from collections import deque
        print(create_df_from_item(deque([1, 2, 3]), 'a'))
        print(np.array([1, 2, 3])[0])
        print(create_df_from_item(np.array([1, 2, 3])[0], 'a'))
        print(create_df_from_item(pd.Series([1, 2, 3]).iloc[0], 'a'))


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
