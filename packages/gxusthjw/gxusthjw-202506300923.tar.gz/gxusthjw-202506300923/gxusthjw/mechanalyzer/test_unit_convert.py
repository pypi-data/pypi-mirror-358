#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_unit_convert.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试unit_convert.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/13     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
from typing import Union

import numpy as np

from ..commons import NumberSequence, Number

from .unit_convert import (length_unit_to_mm,
                           time_unit_to_s,
                           force_unit_to_cn,
                           area_unit_to_mm2,
                           speed_unit_to_mms)


# ==================================================================
# noinspection DuplicatedCode
def speed_unit_to_mms_by_ai(speed: Union[NumberSequence, Number],
                            unit: str) -> Union[NumberSequence, Number]:
    """
    将指定单位的速度数据转换为以毫米每秒（mm/s）为单位的速度数据。

    支持的单位包括：'m/h', 'dm/h', 'cm/h', 'mm/h',
                   'm/min', 'dm/min', 'cm/min', 'mm/min',
                   'm/s', 'dm/s', 'cm/s', 'mm/s'。
    上述单位符号全部都是大小写敏感的。

    :param speed: 指定的速度数据。
    :param unit: 指定速度数据的单位，大小写敏感。
    :return: 以毫米每秒（mm/s）为单位的速度数据。
    """
    # 单位到转换因子的映射
    conversion_factors = {
        "m/h": 1000 / 3600,
        "dm/h": 100 / 3600,
        "cm/h": 10 / 3600,
        "mm/h": 1 / 3600,
        "m/min": 1000 / 60,
        "dm/min": 100 / 60,
        "cm/min": 10 / 60,
        "mm/min": 1 / 60,
        "m/s": 1000,
        "dm/s": 100,
        "cm/s": 10,
        "mm/s": 1,
    }
    if not isinstance(speed, (int, float)):
        speed = np.asarray(speed)
    # 获取转换因子，如果单位不在映射中则抛出异常
    factor = conversion_factors.get(unit)
    if factor is None:
        raise ValueError(f"Unsupported unit: {unit}, "
                         f"Expect one of {list(conversion_factors.keys())}")
    # 返回转换后的速度
    return speed * factor


class TestUnitConvert(unittest.TestCase):
    """
    测试unit_convert.py。
    """

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
    def test_length_unit_to_mm(self):
        self.assertEqual(length_unit_to_mm(1, "mm"), 1)
        self.assertEqual(length_unit_to_mm(1, "cm"), 10)
        self.assertEqual(length_unit_to_mm(1, "m"), 1000)
        self.assertEqual(length_unit_to_mm(1, "dm"), 100)

        self.assertEqual(length_unit_to_mm(1.0, "mm"), 1)
        self.assertEqual(length_unit_to_mm(1.0, "cm"), 10)
        self.assertEqual(length_unit_to_mm(1.0, "m"), 1000)
        self.assertEqual(length_unit_to_mm(1.0, "dm"), 100)

        self.assertEqual(length_unit_to_mm((1, 2), "mm"), (1, 2))
        self.assertEqual(length_unit_to_mm((1, 2), "cm"), (10, 20))
        self.assertEqual(length_unit_to_mm((1, 2), "m"), (1000, 2000))
        self.assertEqual(length_unit_to_mm((1, 2), "dm"), (100, 200))
        self.assertTrue(isinstance(length_unit_to_mm((1, 2), "dm"), tuple))

        self.assertEqual(length_unit_to_mm([1, 2], "mm"), [1, 2])
        self.assertEqual(length_unit_to_mm([1, 2], "cm"), [10, 20])
        self.assertEqual(length_unit_to_mm([1, 2], "m"), [1000, 2000])
        self.assertEqual(length_unit_to_mm([1, 2], "dm"), [100, 200])
        self.assertTrue(isinstance(length_unit_to_mm([1, 2], "dm"), list))

        self.assertTrue(np.allclose(length_unit_to_mm(np.array([1, 2]), "mm"), np.array([1, 2])))
        self.assertTrue(np.allclose(length_unit_to_mm(np.array([1, 2]), "cm"), np.array([10, 20])))
        self.assertTrue(np.allclose(length_unit_to_mm(np.array([1, 2]), "m"), np.array([1000, 2000])))
        self.assertTrue(np.allclose(length_unit_to_mm(np.array([1, 2]), "dm"), np.array([100, 200])))
        self.assertTrue(isinstance(length_unit_to_mm(np.array([1, 2]), "dm"), np.ndarray))

        with self.assertRaises(ValueError) as context:
            length_unit_to_mm(np.array([1, 2]), "km")
        print(context.exception)
        self.assertEqual("Expect unit to be 'm' or 'dm' or 'cm' or 'mm'.", str(context.exception))

    def test_force_unit_to_cn(self):
        self.assertEqual(force_unit_to_cn(1, "N"), 100)
        self.assertEqual(force_unit_to_cn(1, "cN"), 1)

        self.assertEqual(force_unit_to_cn(1.0, "N"), 100.0)
        self.assertEqual(force_unit_to_cn(1.0, "cN"), 1.0)

        self.assertEqual(force_unit_to_cn((1, 2), "N"), (100, 200))
        self.assertEqual(force_unit_to_cn((1, 2), "cN"), (1, 2))
        self.assertTrue(isinstance(force_unit_to_cn((1, 2), "N"), tuple))

        self.assertEqual(force_unit_to_cn([1, 2], "N"), [100, 200])
        self.assertEqual(force_unit_to_cn([1, 2], "cN"), [1, 2])
        self.assertTrue(isinstance(force_unit_to_cn([1, 2], "N"), list))

        self.assertTrue(np.allclose(force_unit_to_cn(np.array([1, 2]), "N"), np.array([100, 200])))
        self.assertTrue(np.allclose(force_unit_to_cn(np.array([1, 2]), "cN"), np.array([1, 2])))
        self.assertTrue(isinstance(force_unit_to_cn(np.array([1, 2]), "N"), np.ndarray))

    def test_area_unit_to_mm2(self):
        self.assertEqual(area_unit_to_mm2(1, "m^2"), 1e6)
        self.assertEqual(area_unit_to_mm2(1, "dm^2"), 1e4)
        self.assertEqual(area_unit_to_mm2(1, "cm^2"), 1e2)
        self.assertEqual(area_unit_to_mm2(1, "mm^2"), 1)

    def test_time_unit_to_s(self):
        self.assertEqual(time_unit_to_s(1, "h"), 3600)
        self.assertEqual(time_unit_to_s(1, "min"), 60)
        self.assertEqual(time_unit_to_s(1, "s"), 1)

    def test_speed_unit_to_mms(self):
        """
        测试speed_unit_to_mms函数。
        """
        self.assertAlmostEqual(2.7778, speed_unit_to_mms(10, 'm/h'), delta=1e-4)
        self.assertAlmostEqual(0.2778, speed_unit_to_mms(10, 'dm/h'), delta=1e-4)
        self.assertAlmostEqual(0.0278, speed_unit_to_mms(10, 'cm/h'), delta=1e-4)
        self.assertAlmostEqual(0.002778, speed_unit_to_mms(10, 'mm/h'), delta=1e-4)
        self.assertAlmostEqual(166.6667, speed_unit_to_mms(10, 'm/min'), delta=1e-4)
        self.assertAlmostEqual(16.66667, speed_unit_to_mms(10, 'dm/min'), delta=1e-4)
        self.assertAlmostEqual(1.66667, speed_unit_to_mms(10, 'cm/min'), delta=1e-4)
        self.assertAlmostEqual(0.1666667, speed_unit_to_mms(10, 'mm/min'), delta=1e-4)
        self.assertEqual(10000, speed_unit_to_mms(10, 'm/s'))
        self.assertEqual(1000, speed_unit_to_mms(10, 'dm/s'))
        self.assertEqual(100, speed_unit_to_mms(10, 'cm/s'))
        self.assertEqual(10, speed_unit_to_mms(10, 'mm/s'))

        with self.assertRaises(ValueError) as exception:
            speed_unit_to_mms(10, 'mm')
        print(exception.exception)

    def test_speed_unit_to_mms_by_ai(self):
        """
        测试speed_unit_to_mms_by_ai函数。
        """
        self.assertAlmostEqual(2.7778, speed_unit_to_mms_by_ai(10, 'm/h'), delta=1e-4)
        self.assertAlmostEqual(0.2778, speed_unit_to_mms_by_ai(10, 'dm/h'), delta=1e-4)
        self.assertAlmostEqual(0.0278, speed_unit_to_mms_by_ai(10, 'cm/h'), delta=1e-4)
        self.assertAlmostEqual(0.002778, speed_unit_to_mms_by_ai(10, 'mm/h'), delta=1e-4)
        self.assertAlmostEqual(166.6667, speed_unit_to_mms_by_ai(10, 'm/min'), delta=1e-4)
        self.assertAlmostEqual(16.66667, speed_unit_to_mms_by_ai(10, 'dm/min'), delta=1e-4)
        self.assertAlmostEqual(1.66667, speed_unit_to_mms_by_ai(10, 'cm/min'), delta=1e-4)
        self.assertAlmostEqual(0.1666667, speed_unit_to_mms_by_ai(10, 'mm/min'), delta=1e-4)
        self.assertEqual(10000, speed_unit_to_mms_by_ai(10, 'm/s'))
        self.assertEqual(1000, speed_unit_to_mms_by_ai(10, 'dm/s'))
        self.assertEqual(100, speed_unit_to_mms_by_ai(10, 'cm/s'))
        self.assertEqual(10, speed_unit_to_mms_by_ai(10, 'mm/s'))

        print(speed_unit_to_mms_by_ai((10, 20, 30, 40), 'cm/h'))


if __name__ == '__main__':
    unittest.main()
