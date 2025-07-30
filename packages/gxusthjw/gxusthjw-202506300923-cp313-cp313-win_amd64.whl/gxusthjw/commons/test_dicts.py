#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_dicts.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试dicts.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

from .dicts import (
    dict_to_str,
)
# 定义 ==============================================================
class TestDicts(unittest.TestCase):
    """
    测试dicts.py。
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

    def test_EmptyKwargs_ReturnsEmptyString(self):
        """
        测试当没有提供任何关键字参数时，函数应返回空字符串。

        此测试用例旨在验证dict_to_str函数在没有接收到任何关键字参数（即kwargs为空）时的行为。
        预期的结果是函数应该返回一个空字符串。
        """
        result = dict_to_str()
        self.assertEqual(result, "")

    def test_NonEmptyKwargs_ReturnsFormattedString(self):
        """
        测试当kwargs非空时，返回正确格式化的字符串。

        该测试用例旨在验证dict_to_str函数在接收非空关键字参数时，
        能够返回预期格式的字符串。具体而言，当传入a=1和b=2作为关键字参数，
        函数应返回"a=1\nb=2"的字符串格式。
        """
        result = dict_to_str(a=1, b=2)
        self.assertEqual(result, "a=1\nb=2")

    def test_CustomDelimiterAndSeparator_ReturnsFormattedString(self):
        """
        测试使用自定义分隔符和连接符时，返回的字符串格式是否正确。

        此测试验证了当提供自定义的delimiter（分隔符）和separator（连接符）时，
        函数dict_to_str能否正确地将字典中的键值对格式化为字符串。预期的输出是
        一个格式化的字符串，其中键值对通过自定义的分隔符连接，键与值之间使用
        自定义的连接符分隔。
        """
        result = dict_to_str(delimiter=":", separator=", ", a=1, b=2)
        self.assertEqual(result, "a:1, b:2")

    def test_DifferentValueTypes_ReturnsFormattedString(self):
        """
        测试不同值类型返回格式化字符串
        当给定的字典包含不同类型的值时，验证dict_to_str函数的行为
        应该返回一个特定格式的字符串，其中包含字典的键值对
        """
        result = dict_to_str(a=1, b="two", c=3.0)
        self.assertEqual(result, "a=1\nb=two\nc=3.0")

    # noinspection PyRedeclaration
    def test_EmptyKwargs_ReturnsEmptyString(self):
        result = dict_to_str()
        self.assertEqual(result, "")

    def test_NonEmptyKwargs_DefaultParameters_ReturnsFormattedString(self):
        result = dict_to_str(key1="value1", key2="value2")
        self.assertEqual(result, "key1=value1\nkey2=value2")

    def test_NonEmptyKwargs_CustomDelimiter_ReturnsFormattedString(self):
        result = dict_to_str(delimiter=":", key1="value1", key2="value2")
        self.assertEqual(result, "key1:value1\nkey2:value2")

    def test_NonEmptyKwargs_CustomDelimiterAndSeparator_ReturnsFormattedString(self):
        result = dict_to_str(delimiter=":", separator=", ", key1="value1", key2="value2")
        self.assertEqual(result, "key1:value1, key2:value2")

    def test_NonEmptyKwargs_DropKey_ReturnsFormattedString(self):
        result = dict_to_str(drop_key=True, key1="value1", key2="value2")
        self.assertEqual(result, "=value1\n=value2")

    def test_NonEmptyKwargs_ValuesConvertedToString_ReturnsFormattedString(self):
        result = dict_to_str(key1=123, key2=45.67, key3=True)
        self.assertEqual(result, "key1=123\nkey2=45.67\nkey3=True")

# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
