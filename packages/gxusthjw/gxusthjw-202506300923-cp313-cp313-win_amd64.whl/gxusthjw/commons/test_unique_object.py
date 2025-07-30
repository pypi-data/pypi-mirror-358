#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_unique_object.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试unique_object.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import string
import unittest

from .unique_object import (
    UniqueIdentifierObject,
    unique_string,
    random_string,
    date_string,
)


# 定义 ==============================================================


class TestUniqueObject(unittest.TestCase):
    """
    测试unique_object.py。
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

    def test_random_string_DefaultLength_CorrectLength(self):
        result = random_string()
        self.assertEqual(len(result), 10)

    def test_random_string_SpecifiedLength_CorrectLength(self):
        result = random_string(5)
        self.assertEqual(len(result), 5)

    def test_random_string_LengthZero_RaisesValueError(self):
        with self.assertRaises(ValueError):
            random_string(0)

    def test_random_string_NegativeLength_RaisesValueError(self):
        with self.assertRaises(ValueError):
            random_string(-1)

    # noinspection PyTypeChecker
    def test_random_string_NonIntegerLength_RaisesTypeError(self):
        with self.assertRaises(TypeError):
            random_string(5.5)
        with self.assertRaises(TypeError):
            random_string("ten")

    def test_random_string_ValidCharacters(self):
        result = random_string(100)
        valid_characters = string.ascii_letters + string.digits + "_"
        for char in result:
            self.assertIn(char, valid_characters)

    def test_unique_string(self):
        print(unique_string())

    def test_date_string(self):
        print(date_string())

    def test_random_string(self):
        print(random_string(1))
        print(random_string(2))
        print(random_string(3))
        print(random_string(4))

        with self.assertRaises(ValueError) as exception:
            print(random_string(0))
        print(exception.exception.args[0])

    # noinspection PyPropertyAccess,PyUnresolvedReferences
    def test_unique_identifier_object(self):
        for i in range(100):
            uo = UniqueIdentifierObject()
            print(uo.identifier)


if __name__ == "__main__":
    unittest.main()
