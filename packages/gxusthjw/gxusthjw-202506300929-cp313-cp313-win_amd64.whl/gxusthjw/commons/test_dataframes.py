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
    create_df_from_item,
    create_df_from_dict,
    merge_df,
    merge_dfs
)


# 定义 ==============================================================
__DEFAULT_ITEM_NAME_PREFIX__ = "item"

class TestDataFrames(unittest.TestCase):
    """
    测试dataframes.py。
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

    def test_create_df_from_item(self):
        result = create_df_from_item(123)
        expected = pd.DataFrame({"item": [123]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

        result1 = create_df_from_item(123.0)
        expected1 = pd.DataFrame({"item": [123.0]})
        pd.testing.assert_frame_equal(result1, expected1, check_dtype=False)

        result2 = create_df_from_item(np.array([123])[0])
        expected2 = pd.DataFrame({"item": [123.0]})
        pd.testing.assert_frame_equal(result2, expected2, check_dtype=False)

        result3 = create_df_from_item(pd.Series([123])[0])
        expected3 = pd.DataFrame({"item": [123.0]})
        pd.testing.assert_frame_equal(result3, expected3, check_dtype=False)

        result4 = create_df_from_item(np.array([123.0, 254.0]), "test_column")
        expected4 = pd.DataFrame({"test_column": [123.0, 254.0]})
        pd.testing.assert_frame_equal(result4, expected4, check_dtype=False)

        result5 = create_df_from_item({1, 2, 3}, "test_column")
        expected5 = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result5, expected5, check_dtype=False)

        result6 = create_df_from_item(frozenset([1, 2, 3]), "test_column")
        expected6 = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result6, expected6, check_dtype=False)

        # 设置最大长度为3
        d = deque(maxlen=3)
        d.append(1)
        d.append(2)
        d.append(3)
        d.append(4)  # 自动移除最左边的1
        result7 = create_df_from_item(d, "test_column")
        expected7 = pd.DataFrame({"test_column": [2, 3, 4]})
        pd.testing.assert_frame_equal(result7, expected7, check_dtype=False)

        # 声明一个整数类型的数组，并初始化一些元素
        arr = array.array('i', [1, 2, 3, 4, 5])
        result8 = create_df_from_item(arr, "test_column")
        expected8 = pd.DataFrame({"test_column": [1, 2, 3, 4, 5]})
        pd.testing.assert_frame_equal(result8, expected8, check_dtype=False)

        result9 = create_df_from_item({'a':[1, 2, 3, 4, 5]}, "a")
        expected9 = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
        pd.testing.assert_frame_equal(result9, expected9, check_dtype=False)

        result9 = create_df_from_item({'a': 1,  'b': 2}, "f")
        print(result9)

        result10 = create_df_from_item(np.array(["1","2"]), "test_column")
        expected10 = pd.DataFrame({"test_column": ["1","2"]})
        pd.testing.assert_frame_equal(result10, expected10, check_dtype=False)

    # region TC02: data 为不可迭代对象（int），未提供 name，使用默认列名
    def test_create_df_from_item_non_iterable_no_name(self):
        result = create_df_from_item(42)
        expected = pd.DataFrame({__DEFAULT_ITEM_NAME_PREFIX__: [42]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
    # endregion

    # region TC03: data 为字符串（不可迭代），提供 name
    def test_create_df_from_item_str_with_name(self):
        result = create_df_from_item("hello", name="text")
        expected = pd.DataFrame({"text": ["hello"]})
        pd.testing.assert_frame_equal(result, expected)
    # endregion

    # region TC04: data 为 set，未提供 name
    def test_create_df_from_item_set_no_name(self):
        result = create_df_from_item({1, 2, 3})
        self.assertEqual(len(result), 3)
        self.assertEqual(result.columns[0], __DEFAULT_ITEM_NAME_PREFIX__)
    # endregion

    # region TC05: data 为 frozenset，未提供 name
    def test_create_df_from_item_frozenset_no_name(self):
        result = create_df_from_item(frozenset([1, 2, 3]))
        self.assertEqual(len(result), 3)
        self.assertEqual(result.columns[0], __DEFAULT_ITEM_NAME_PREFIX__)
    # endregion

    # region TC06: data 为 dict，name 存在于 dict 中
    def test_create_df_from_item_dict_with_valid_key(self):
        data = {"a": [1, 2], "b": [3, 4]}
        result = create_df_from_item(data, name="a")
        expected = pd.DataFrame({"a": [1, 2]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
    # endregion

    # region TC07: data 为 dict，name 不存在于 dict 中
    def test_create_df_from_item_dict_with_invalid_key(self):
        data = {"a": [1, 2], "b": [3, 4]}
        with self.assertRaises(ValueError):
            create_df_from_item(data, name="c")
    # endregion

    # region TC08: data 为 list，未提供 name
    def test_create_df_from_item_list_no_name(self):
        result = create_df_from_item([1, 2, 3])
        expected = pd.DataFrame({__DEFAULT_ITEM_NAME_PREFIX__: [1, 2, 3]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
    # endregion

    # region TC09: data 为 tuple，未提供 name
    def test_create_df_from_item_tuple_no_name(self):
        result = create_df_from_item((1, 2, 3))
        expected = pd.DataFrame({__DEFAULT_ITEM_NAME_PREFIX__: [1, 2, 3]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
    # endregion

    # region TC10: data 为 range，未提供 name
    def test_create_df_from_item_range_no_name(self):
        result = create_df_from_item(range(3))
        expected = pd.DataFrame({__DEFAULT_ITEM_NAME_PREFIX__: [0, 1, 2]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)
    # endregion

    # region TC12: data 为多维数组，应抛出 ValueError
    def test_create_df_from_item_multidimensional_data_raises_value_error(self):
        data = [[1, 2], [3, 4]]
        with self.assertRaises(ValueError) as cm:
            create_df_from_item(data)
        self.assertEqual(str(cm.exception), "Failed to convert data to one-dimensional numpy array.")
    # endregion

    # region TC13: data 无法转换为 numpy array（例如自定义类实例）
    def test_create_df_from_item_unconvertible_data_raises_value_error(self):
        class CustomObject:
            pass

        obj = CustomObject()
        res = create_df_from_item(obj)
        print(res)
    # endregion

    def test_create_df_from_item_NonIterableData_ConvertsToList(self):
        result = create_df_from_item(123, "test_column")
        expected = pd.DataFrame({"test_column": [123]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_create_df_from_item_StringData_ConvertsToList(self):
        result = create_df_from_item("test", "test_column")
        expected = pd.DataFrame({"test_column": ["test"]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_create_df_from_item_SetData_ConvertsToList(self):
        result = create_df_from_item({1, 2, 3}, "test_column")
        expected = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_create_df_from_item_FrozenSetData_ConvertsToList(self):
        result = create_df_from_item(frozenset({1, 2, 3}), "test_column")
        expected = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_create_df_from_item_IterableData_KeepsAsIs(self):
        result = create_df_from_item([1, 2, 3], "test_column")
        expected = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result, expected,check_dtype=False)

    def test_create_df_from_item_TupleData_KeepsAsIs(self):
        result = create_df_from_item((1, 2, 3), "test_column")
        expected = pd.DataFrame({"test_column": [1, 2, 3]})
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_create_df_from_dict_ValidDict_ReturnsDataFrame(self):
        data = {'a': [1, 2, 3], 'b': [4, 5, 6]}
        result = create_df_from_dict(data)
        expected = pd.DataFrame(data)
        print(result)
        print(expected)
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_create_df_from_dict_EmptyDict_ReturnsEmptyDataFrame(self):
        data = {}
        result = create_df_from_dict(data)
        expected = pd.DataFrame()
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    # noinspection PyTypeChecker
    def test_create_df_from_dict_NonDictInput_RaisesValueError(self):
        with self.assertRaises(ValueError):
            create_df_from_dict([1, 2, 3])

    def test_create_df_from_dict_SingleKeyValuePair_ReturnsDataFrame(self):
        data = {'a': [1, 2, 3]}
        result = create_df_from_dict(data)
        print(result)
        print(result.dtypes)
        expected = pd.DataFrame(data)
        print(expected)
        print(expected.dtypes)
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_merge_df_ValidDataFrames_ReturnsMergedDataFrame(self):
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"C": [5, 6], "D": [7, 8]})
        expected_df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8]})
        result_df = merge_df(df1, df2)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_merge_df_ColumnNameConflict_ReturnsMergedDataFrameWithConflictResolution(self):
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"B": [5, 6], "C": [7, 8]})
        expected_df = pd.DataFrame({"A": [1, 2], "B": [5, 6], "C": [7, 8]})
        result_df = merge_df(df1, df2)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_merge_df_EmptyDataFrames_ReturnsEmptyDataFrame(self):
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        expected_df = pd.DataFrame()
        result_df = merge_df(df1, df2)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_merge_df_OneEmptyDataFrame_ReturnsNonEmptyDataFrame(self):
        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = pd.DataFrame()
        expected_df = pd.DataFrame({"A": [1, 2]})
        result_df = merge_df(df1, df2)
        pd.testing.assert_frame_equal(result_df, expected_df)

    # noinspection PyTypeChecker
    def test_merge_df_NonDataFrameInput_RaisesValueError(self):
        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = "not a DataFrame"
        with self.assertRaises(ValueError):
            merge_df(df1, df2)

    def test_merge_dfs_TwoDataFrames_MergedCorrectly(self):
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"C": [5, 6], "D": [7, 8]})
        result = merge_dfs(df1, df2)
        expected = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8]})
        pd.testing.assert_frame_equal(result, expected)

    def test_merge_dfs_MultipleDataFrames_MergedCorrectly(self):
        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = pd.DataFrame({"B": [3, 4]})
        df3 = pd.DataFrame({"C": [5, 6]})
        result = merge_dfs(df1, df2, df3)
        expected = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
        pd.testing.assert_frame_equal(result, expected)

    def test_merge_dfs_DuplicateColumnNames_LastColumnWins(self):
        df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = pd.DataFrame({"B": [5, 6], "C": [7, 8]})
        result = merge_dfs(df1, df2)
        expected = pd.DataFrame({"A": [1, 2], "B": [5, 6], "C": [7, 8]})
        pd.testing.assert_frame_equal(result, expected)

    def test_merge_dfs_EmptyDataFrames_ReturnsEmptyDataFrame(self):
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        result = merge_dfs(df1, df2)
        expected = pd.DataFrame()
        pd.testing.assert_frame_equal(result, expected)

    def test_merge_dfs_DifferentIndices_MergedCorrectly(self):
        df1 = pd.DataFrame({"A": [1, 2]}, index=[0, 1])
        df2 = pd.DataFrame({"B": [3, 4]}, index=[1, 2])
        result = merge_dfs(df1, df2)
        expected = pd.DataFrame({"A": [1, 2, None], "B": [None, 3, 4]}, index=[0, 1, 2])
        pd.testing.assert_frame_equal(result, expected)


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
