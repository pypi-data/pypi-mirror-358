#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_specimen.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试test_specimen.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# -----------------------------------------------------------------
# 导包 =============================================================
import unittest

from .specimen import Specimen


# 定义 =============================================================
class SpecimenImpl(Specimen):
    """
    处于测试目的，对Specimen进行简单的继承，并实现其抽象方法。
    """

    def __init__(self, *args, **kwargs):
        super(SpecimenImpl, self).__init__(*args, **kwargs)


class TestSpecimen(unittest.TestCase):
    """
    测试specimen.py。
    """

    # ==============================================================
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

    # ==============================================================

    # noinspection DuplicatedCode,PyUnresolvedReferences
    def test_init(self):
        td = SpecimenImpl()
        self.assertEqual('specimen', td.specimen_name)
        self.assertEqual('specimen_0', td.sample_name)

        td1 = SpecimenImpl(specimen_name='a')
        self.assertEqual('a', td1.specimen_name)
        self.assertEqual('a_0', td1.sample_name)

        td3 = SpecimenImpl(specimen_name='c', sample_name="d")
        self.assertEqual('c', td3.specimen_name)
        self.assertEqual('d', td3.sample_name)

        td4 = SpecimenImpl(aa=10)
        self.assertEqual(10, td4.aa)
        self.assertEqual('specimen', td4.specimen_name)
        self.assertEqual('specimen_0', td4.sample_name)

        td5 = SpecimenImpl(specimen_name='a', aa=10)
        self.assertEqual(10, td5.aa)
        self.assertEqual('a', td5.specimen_name)
        self.assertEqual('a_0', td5.sample_name)

        td7 = SpecimenImpl(specimen_name='c', sample_name='c_5', aa=10)
        self.assertEqual(10, td7.aa)
        self.assertEqual('c', td7.specimen_name)
        self.assertEqual('c_5', td7.sample_name)

        td8 = SpecimenImpl(specimen_name='c', sample_name='c_5', aa=10)
        self.assertEqual(10, td8.aa)
        self.assertEqual('c', td8.specimen_name)
        self.assertEqual('c_5', td8.sample_name)

        td8.specimen_name = "h"
        self.assertEqual(10, td8.aa)
        self.assertEqual('h', td8.specimen_name)
        self.assertEqual('c_5', td8.sample_name)

        td8.sample_name = "nn"
        self.assertEqual(10, td8.aa)
        self.assertEqual('h', td8.specimen_name)
        self.assertEqual('nn', td8.sample_name)


if __name__ == '__main__':
    unittest.main()
