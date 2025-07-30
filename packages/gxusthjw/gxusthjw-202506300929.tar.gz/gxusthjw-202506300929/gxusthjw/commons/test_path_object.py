#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_path_object.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试path_object.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import shutil
import unittest
from pathlib import Path
from .path_object import (
    PathObject,
)


# ==================================================================
class TestPathObject(unittest.TestCase):
    """
    测试`PathObject`类。
    """

    # region
    # --------------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        # 设置一个临时文件路径用于测试
        self.temp_file_path = Path('temp_test_file.txt')
        self.temp_folder_path = Path('temp_test_folder')

        # 确保测试开始时文件和文件夹不存在
        if self.temp_file_path.exists():
            self.temp_file_path.unlink()
        if self.temp_folder_path.exists():
            shutil.rmtree(self.temp_folder_path)
        print("\n\n-----------------------------------------------------")

    def tearDown(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        # 测试结束后清理临时文件和文件夹
        if self.temp_file_path.exists():
            self.temp_file_path.unlink()
        if self.temp_folder_path.exists():
            shutil.rmtree(self.temp_folder_path)
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

    def test_init_with_string(self):
        path_obj = PathObject('some/path')
        self.assertEqual(path_obj.path, Path('some/path'))

    def test_init_with_path_object(self):
        path_obj = PathObject(Path('some/path'))
        self.assertEqual(path_obj.path, Path('some/path'))

    def test_validate(self):
        path_obj = PathObject('some/path')
        self.assertTrue(path_obj.validate)

    def test_path_property(self):
        path_obj = PathObject('some/path')
        self.assertIsInstance(path_obj.path, Path)

    def test_path_str_property(self):
        path_obj = PathObject('some/path')
        self.assertEqual(path_obj.path_str, str(Path('some/path').resolve()))

    def test_parent_property(self):
        path_obj = PathObject('some/path/to/file.txt')
        self.assertEqual(path_obj.parent.path, Path('some/path/to').resolve())

    def test_is_file_property(self):
        path_obj = PathObject('some/path')
        self.assertFalse(path_obj.is_file)

        # 创建一个临时文件并测试
        self.temp_file_path.touch()
        path_obj = PathObject(self.temp_file_path)
        self.assertTrue(path_obj.is_file)

    def test_is_folder_property(self):
        path_obj = PathObject('some/path')
        self.assertFalse(path_obj.is_folder)

        # 创建一个临时文件夹并测试
        self.temp_folder_path.mkdir()
        path_obj = PathObject(self.temp_folder_path)
        self.assertTrue(path_obj.is_folder)

    def test_exists_property(self):
        path_obj = PathObject('some/path')
        self.assertFalse(path_obj.exists)

        # 创建一个临时文件并测试
        self.temp_file_path.touch()
        path_obj = PathObject(self.temp_file_path)
        self.assertTrue(path_obj.exists)

        # 创建一个临时文件夹并测试
        self.temp_folder_path.mkdir()
        path_obj = PathObject(self.temp_folder_path)
        self.assertTrue(path_obj.exists)

    def test_name_property(self):
        path_obj = PathObject('some/path/to/file.txt')
        self.assertEqual(path_obj.name, 'file.txt')

    def test_str_representation(self):
        path_obj = PathObject('some/path/to/file.txt')
        self.assertEqual(str(path_obj), str(Path('some/path/to/file.txt')))
        self.assertEqual(path_obj.name, 'file.txt')


# ==================================================================
if __name__ == '__main__':
    unittest.main()
