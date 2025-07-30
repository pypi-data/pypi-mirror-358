#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_file_info.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试file_info.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import os
import unittest

from .file_info import (
    encoding_of,
    info_of,
    module_info_of,
    FileInfo
)


# 定义 ==============================================================
class TestFileInfo(unittest.TestCase):
    """
    测试file_info.py。
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

    def test_encoding_of(self):
        """
        测试`encoding_of`方法。
        """
        # --------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this_file_path: %s' % this_file_path)

        test_data_folder = "test_data/file_info"
        test_data_path = os.path.join(this_file_path, test_data_folder)
        # --------------------------------------------------------------
        print("--------------------------------------------------------------")
        ansi_file = os.path.join(test_data_path, "ansi_file.txt")
        ansi_file_encoding = encoding_of(ansi_file)
        print("ansi_file_encoding(type({})):{}".format(type(ansi_file_encoding),
                                                       ansi_file_encoding))
        self.assertEqual(ansi_file_encoding, "ascii")


        gb2312_file = os.path.join(test_data_path, "gb2312_file.txt")
        gb2312_file_encoding = encoding_of(gb2312_file)
        print("gb2312_file_encoding(type({})):{}".format(type(gb2312_file_encoding),
                                                         gb2312_file_encoding))
        self.assertEqual(gb2312_file_encoding, "IBM855")

        gb18030_file = os.path.join(test_data_path, "gb18030_file.txt")
        gb18030_file_encoding = encoding_of(gb18030_file)
        print("gb18030_file_encoding(type({})):{}".format(type(gb18030_file_encoding),
                                                       gb18030_file_encoding))
        self.assertEqual(gb18030_file_encoding, "IBM855")

        gkb_file = os.path.join(test_data_path, "gkb_file.txt")
        gkb_file_encoding = encoding_of(gkb_file)
        print("gkb_file_encoding(type({})):{}".format(type(gkb_file_encoding),
                                                      gkb_file_encoding))
        self.assertEqual(gkb_file_encoding, "GB2312")

        utf8_file = os.path.join(test_data_path, "utf8_file.txt")
        utf8_file_encoding = encoding_of(utf8_file)
        print("utf8_file_encoding(type({})):{}".format(type(utf8_file_encoding),
                                                       utf8_file_encoding))
        self.assertEqual(utf8_file_encoding, "utf-8")

        utf16_file = os.path.join(test_data_path, "utf16_file.txt")
        utf16_file_encoding = encoding_of(utf16_file)
        print("utf16_file_encoding(type({})):{}".format(type(utf16_file_encoding),
                                                        utf16_file_encoding))
        self.assertEqual(utf16_file_encoding, "UTF-16BE")

        utf16be_file = os.path.join(test_data_path, "utf16be_file.txt")
        utf16be_file_encoding = encoding_of(utf16be_file)
        print("utf16be_file_encoding(type({})):{}".format(type(utf16be_file_encoding),
                                                          utf16be_file_encoding))
        self.assertEqual(utf16be_file_encoding, "UTF-16BE")

        utf16le_file = os.path.join(test_data_path, "utf16le_file.txt")
        utf16le_file_encoding = encoding_of(utf16le_file)
        print("utf16le_file_encoding(type({})):{}".format(type(utf16le_file_encoding),
                                                          utf16le_file_encoding))
        self.assertEqual(utf16le_file_encoding, "UTF-16LE")

    # noinspection PyUnresolvedReferences
    def test_info_of(self):
        """
        测试`info_of`方法。
        """
        file = info_of('c:/a.txt', encoding="GBT", C="C",
                       O=20.2, E=True)
        print(file)
        self.assertEqual(file, "c:/a.txt")
        print(str(file))
        print(repr(file))
        self.assertEqual(repr(file),
                         "FileInfo{'dir_path': 'c:\\\\', "
                         "'base_name': 'a', 'ext_name': 'txt', 'full_name': 'a.txt', "
                         "'full_path': 'c:\\\\a.txt', 'encoding': 'GBT', 'C': 'C', 'O': 20.2, "
                         "'E': True}")


        print(file.C)
        self.assertEqual(file.C, "C")
        print(file.E)
        self.assertEqual(file.E, True)
        print(file.O)
        self.assertEqual(file.O, 20.2)

    def test_module_info_of(self):
        """
        测试`module_info_of`方法。
        """
        file = module_info_of(__name__)
        print(file)
        print(str(file))
        print(repr(file))

        file = module_info_of(__name__)
        print(file)
        print(str(file))
        print(repr(file))

        file = module_info_of(__name__)
        print(file)
        print(str(file))
        print(repr(file))

        file = module_info_of('os')
        print(file)
        print(str(file))
        print(repr(file))

        file = module_info_of('inspect')
        print(file)
        print(str(file))
        print(repr(file))

        file = module_info_of('chardet')
        print(file)
        print(str(file))
        print(repr(file))

    # noinspection PyUnresolvedReferences
    def test_FileInfo(self):
        """
        测试`FileInfo`方法。
        """
        file = FileInfo("c:/", "a",
                        "txt", encoding="GBT", C="C",
                        O=20.2, E=True)
        print(file)
        self.assertEqual(str(file), "c:\\a.txt")
        print(str(file))
        self.assertEqual(repr(file),
                         "FileInfo{'dir_path': 'c:\\\\', "
                         "'base_name': 'a', 'ext_name': 'txt', 'full_name': 'a.txt', "
                         "'full_path': 'c:\\\\a.txt', 'encoding': 'GBT', 'C': 'C', 'O': 20.2, "
                         "'E': True}")
        print(repr(file))

        print(file.C)
        self.assertEqual(file.C, "C")
        print(file.E)
        self.assertEqual(file.E, True)
        print(file.O)
        self.assertEqual(file.O, 20.2)

    # noinspection PyUnresolvedReferences
    def test_FileInfo_repr(self):
        """
        测试`FileInfo`
        """
        file = FileInfo("c:/", "a",
                        "txt", encoding="GBT", C="C",
                        O=20.2, E=True)
        print(file)
        self.assertEqual(str(file), "c:\\a.txt")
        print(str(file))
        self.assertEqual(repr(file),
                         "FileInfo{'dir_path': 'c:\\\\', "
                         "'base_name': 'a', 'ext_name': 'txt', 'full_name': 'a.txt', "
                         "'full_path': 'c:\\\\a.txt', 'encoding': 'GBT', 'C': 'C', 'O': 20.2, "
                         "'E': True}")
        print(repr(file))

        print(file.C)
        self.assertEqual(file.C, "C")
        print(file.E)
        self.assertEqual(file.E, True)
        print(file.O)
        self.assertEqual(file.O, 20.2)

    def test_FileInfo_make_file(self):
        """
        测试`FileInfo`
        """
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this_file_path: %s' % this_file_path)

        test_out = "test_out/file_info"

        dictionary_path = os.path.join(this_file_path, test_out)

        file = FileInfo(dictionary_path, "make_a_file1",
                        "txt", encoding="GBK", C="C",
                        O=20.2, E=True)

        # file.make_directory()
        file.make_file()



# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
