#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_data_table.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_table.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

import numpy as np
import pandas as pd

from .data_table import DataTable


# 定义 ==============================================================
class TestDataTable(unittest.TestCase):
    """
    测试data_table.py。
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

    def test_init(self):
        table1 = DataTable()
        self.assertEqual(table1.num_items, 0)
        self.assertEqual(table1.shape, (0, 0))
        self.assertTrue(table1.is_empty)
        table1.print()

        table2 = DataTable(data_dict={"a": [1, 2, 3], "b": [4, 5, 6]})
        table2.print()

    def test_item_name_prefix(self):
        """
        测试：data_capsule.__DEFAULT_ITEM_NAME_PREFIX__
        """
        from . import data_table
        print(data_table.__DEFAULT_ITEM_NAME_PREFIX__)
        self.assertEqual("item_", data_table.__DEFAULT_ITEM_NAME_PREFIX__)

    def test_constructor(self):
        """
        测试DataCapsule的构造方法1。
        """
        pd.set_option('display.max_columns', None)
        # 设置pandas显示所有行
        pd.set_option('display.max_rows', None)
        # 设置pandas显示所有字符
        pd.set_option('display.max_colwidth', None)
        print(bool(None))

        print("-------------------------------------")
        table1 = DataTable()
        self.assertEqual(True, table1.is_empty)
        print(table1.shape)
        self.assertEqual((0, 0), table1.shape)
        # self.assertEqual(table1)
        table1.print()
        print("-------------------------------------")

        table2 = DataTable(1)
        self.assertEqual(False, table2.is_empty)
        print(table2.shape)
        self.assertEqual((1, 1), table2.shape)
        table2.print()
        print("-------------------------------------")

        table3 = DataTable(1, 2)
        print(table3.shape)
        self.assertEqual((1, 2), table3.shape)
        table3.print()
        print("-------------------------------------")

        table4 = DataTable(1, 2, [1])
        print(table4.shape)
        self.assertEqual((1, 3), table4.shape)
        table4.print()
        print("-------------------------------------")

        table5 = DataTable([1])
        print(table5.shape)
        table5.print()
        print("-------------------------------------")

        table6 = DataTable([1, 2])
        print(table6.shape)
        table6.print()
        print("-------------------------------------")

        table7 = DataTable([1], [1])
        print(table7.shape)
        table7.print()
        print("-------------------------------------")

        table8 = DataTable([1], [1, 2])
        print(table8.shape)
        table8.print()
        print("-------------------------------------")

        table9 = DataTable([1, 3, 5], [1, 2])
        print(table9.shape)
        table9.print()
        print("-------------------------------------")

        table10 = DataTable([1, 3, 5], [1, 2], 2)
        print(table10.shape)
        table10.print()
        print("-------------------------------------")

        table11 = DataTable(1, 3, 'a', [1, 3, 5], [1, 2], 2)
        print(table11.shape)
        table11.print()
        print("-------------------------------------")

        table12 = DataTable(4, '5', [object], [1, 3, 5], [1, 2], 2)
        print(table12.shape)
        table12.print()
        print("-------------------------------------")

        table13 = DataTable(1, 3, True, [1, 3, 5], [1, 2], 2)
        print(table13.shape)
        table13.print()
        print("-------------------------------------")

        table14 = DataTable(4, '5', object, [1, 3, 5], [1, 2], 2)
        print(table14.shape)
        table14.print()
        print("-------------------------------------")

        table15 = DataTable(4, '5', table14, [1, 3, 5], [1, 2], 2)
        print(table15.shape)
        table15.print()
        print("-------------------------------------")

        table16 = DataTable(None)
        print(table16.shape)
        table16.print()

    def test_constructor2(self):
        table1 = DataTable(1, item_names={0: 'one'})
        print(table1.shape)
        table1.print()
        table2 = DataTable(1, item_names={0: 'one', 1: 'two'})
        print(table2.shape)
        table2.print()

        table3 = DataTable(1, 2, 3, 4, item_names={0: 'one', 1: 'two'})
        print(table3.shape)
        table3.print()

        table4 = DataTable(1, 2, 3, 4, item_names={1: 'one', 2: 'two'})
        print(table4.shape)
        table4.print()

        table5 = DataTable(1, 2, 3, 4, item_names={1: 'one', 2: 'two', 3: 'three', 5: 'five'})
        print(table5.shape)
        table5.print()

    def test_constructor3(self):
        table1 = DataTable(1, item_names=['one'])
        print(table1.shape)
        table1.print()

        table2 = DataTable(1,
                             item_names=['one', 'two'])
        print(table2.shape)
        table2.print()

        table3 = DataTable(1, 2, 3, 4,
                             item_names=['one', 'two'])
        print(table3.shape)
        table3.print()

        table4 = DataTable(1, 2, 3, 4,
                             item_names=['one', 'two', 'three'])
        print(table4.shape)
        table4.print()

        table5 = DataTable(1, 2, 3, 4,
                             item_names=['one', 'two', 'three', 'five'])
        print(table5.shape)
        table5.print()

    def test_update(self):
        table = DataTable()
        print(table.shape)
        table.print()
        table.update(2, '0')
        print(table.shape)
        table.print()

        table2 = DataTable(1, 2, 3, 4,
                             item_names=['one', 'two', 'three', 'five'])
        print(table2.shape)
        table2.print()
        table2.update(2, '0')
        print(table2.shape)
        table2.print()

        table3 = DataTable(1, 2, 3, 4,
                             item_names=['one', 'two', 'three', 'five'])
        print(table3.shape)
        table3.print()
        table3.update([2, 0, 3, 4], '0')
        print(table3.shape)
        table3.print()

        table4 = DataTable(1, 2, 3, 4,
                             item_names=['one', 'two', 'three', 'five'])
        print(table4.shape)
        table4.print()
        table4.update([2, 0, 3, 4])
        table4.update([2, 0, 3, 4])
        table4.update([2, 0, 3, 4])
        table4.update([2, 0, 3, 4])
        print(table4.shape)
        table4.print()

    def test_get_item(self):
        table3 = DataTable(1, [1, 2], None, (4, 5, 6, 7), np.arange(20),
                           item_names=['one', 'two', 'three', 'five'])
        table3.print({'display.max_columns': None, 'display.max_rows': None,
                      'display.max_colwidth': None})

        print(table3.get('one'))
        print(table3.get('two'))
        print(table3.get('three'))
        print(table3.get('five'))
        print(table3.get('item_4'))

        print(table3.get(0))
        print(table3.get(1))
        print(table3.get(2))
        print(table3.get(3))
        print(table3.get(4))

    def test_update_data(self):
        table3 = DataTable(1, [1, 2], None, (4, 5, 6, 7), np.arange(20),
                           item_names=['one', 'two', 'three', 'five'])
        table3.print({'display.max_columns': None, 'display.max_rows': None,
                      'display.max_colwidth': None})
        table3.updates(1, 2, 3, 4,
                       item_names=['one', 'two', 'three', 'five'])
        table3.print({'display.max_columns': None, 'display.max_rows': None,
                      'display.max_colwidth': None})

    def test_update_data2(self):
        table3 = DataTable(1, [1, 2], None, (4, 5, 6, 7), np.arange(20),
                           item_names=['one', 'two', 'three', 'five'])
        table3.print({'display.max_columns': None, 'display.max_rows': None,
                      'display.max_colwidth': None})
        table3.updates(1, 2, 3, 4,
                       item_names=['one1', 'two1', 'three1', 'five1'])
        table3.print({'display.max_columns': None, 'display.max_rows': None,
                      'display.max_colwidth': None})


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
