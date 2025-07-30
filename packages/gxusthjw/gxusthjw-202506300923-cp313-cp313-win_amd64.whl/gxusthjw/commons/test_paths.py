#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_paths.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试paths.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/15     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import os
import tempfile
import shutil
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from .paths import (
    UniquePathGenerationError,
    gen_unique_path,
)


# 定义 ==============================================================
class TestPaths(unittest.TestCase):
    """
    测试paths.py。
    """

    # region
    # --------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        self.test_dir = tempfile.mkdtemp()
        print("\n\n-----------------------------------------------------")

    def tearDown(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        shutil.rmtree(self.test_dir)
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

    def test_basic_file_creation(self):
        """TC01: 基本成功案例 - 无冲突文件"""
        result = gen_unique_path(self.test_dir, "test", ".txt")
        expected_path = os.path.join(self.test_dir, "test.txt")

        # 使用 Path 标准化路径后再比较
        self.assertEqual(Path(result).resolve(), Path(expected_path).resolve())

    def test_conflicting_file_exists(self):
        """TC02: 已有同名文件，需使用_copy1"""
        # 创建一个冲突文件
        conflict_file = os.path.join(self.test_dir, "test.txt")
        open(conflict_file, 'a').close()

        result = gen_unique_path(self.test_dir, "test", ".txt")
        expected_path = os.path.join(self.test_dir, "test_copy1.txt")
        self.assertEqual(Path(result).resolve(), Path(expected_path).resolve())

    def test_create_directory(self):
        """TC03: 生成目录而非文件"""
        # 模拟目标路径的 Path 实例
        target_path = Path(self.test_dir) / "new_folder"

        # 创建 MagicMock 替换 Path 实例的 mkdir 方法
        mock_mkdir = MagicMock()

        # Monkey patch 目标路径的 mkdir 方法
        with patch.object(target_path.__class__, 'mkdir', mock_mkdir):
            result = gen_unique_path(self.test_dir, "new_folder", create=True)
            expected_path = os.path.join(self.test_dir, "new_folder")
            self.assertEqual(Path(result).resolve(), Path(expected_path).resolve())
            # mock_mkdir.assert_called_once_with(exist_ok=False, parents=True)

    def test_do_not_create_file(self):
        """TC04: 不创建文件"""
        result = gen_unique_path(self.test_dir, "test", ".txt")
        full_path = os.path.join(self.test_dir, "test.txt")
        self.assertEqual(Path(result).resolve(), Path(full_path).resolve())
        self.assertFalse(os.path.exists(full_path))

    def test_invalid_basename_type(self):
        """TC05: 参数类型错误 - file_base_name非字符串"""
        with self.assertRaises(TypeError):
            gen_unique_path(self.test_dir, 123)

    def test_empty_basename(self):
        """TC06: 参数错误 - file_base_name为空"""
        with self.assertRaises(ValueError):
            gen_unique_path(self.test_dir, "")

    def test_invalid_max_attempts(self):
        """TC07: 参数错误 - max_attempts无效"""
        with self.assertRaises(ValueError):
            gen_unique_path(self.test_dir, "test", max_attempts=0)

    def test_extension_without_dot(self):
        """TC08: 扩展名未带点号"""
        result = gen_unique_path(self.test_dir, "test", "txt")
        expected_path = os.path.join(self.test_dir, "test.txt")
        self.assertEqual(Path(result).resolve(), Path(expected_path).resolve())

    def test_create_parent_directories(self):
        """TC10: 父目录不存在但create=True"""
        nested_dir = os.path.join(self.test_dir, "nested", "subdir")
        result = gen_unique_path(nested_dir, "testfile", ".txt", create=True)
        expected_path = os.path.join(nested_dir, "testfile.txt")
        self.assertEqual(Path(result).resolve(), Path(expected_path).resolve())
        self.assertTrue(os.path.exists(expected_path))


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
