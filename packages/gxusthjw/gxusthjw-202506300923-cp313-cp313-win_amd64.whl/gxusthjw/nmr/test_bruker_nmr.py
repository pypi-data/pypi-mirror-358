#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_bruker_nmr.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试bruker_nmr.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/16     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import os

from pprint import pprint

from .bruker_nmr import (
    read_bruker,
    read_pdata_bruker,
    ppm_intensity_bruker,
    NmrBruker
)

from ..commons import (
    read_txt
)


# 定义 ==============================================================
class TestBrukerNmr(unittest.TestCase):
    """
    测试bruker_nmr.py。
    """

    # region
    # --------------------------------------------------------------
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

    # --------------------------------------------------------------
    # endregion

    def test_read_bruker(self):
        """
        测试read_bruker。
        """
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_data_folder = "test_data"
        nmr_datas = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', ]
        test_data_path = os.path.join(this_file_path, test_data_folder)
        # ------------------------------------------------------------------
        for nmr_data_index in range(len(nmr_datas)):
            test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
            dic, data = read_bruker(test_data)
            pprint(dic)
            pprint(data)

    def test_read_pdata_bruker(self):
        """
        测试read_pdata_bruker。
        """
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_data_folder = "test_data"
        nmr_datas = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', ]
        test_data_path = os.path.join(this_file_path, test_data_folder)
        # ------------------------------------------------------------------
        for nmr_data_index in range(len(nmr_datas)):
            test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
            dic, data = read_pdata_bruker(test_data)
            pprint(dic)
            pprint(data)

    def test_ppm_intensity_bruker(self):
        """
        测试ppm_intensity_bruker。
        """
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_data_folder = "test_data"
        nmr_datas = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', ]
        test_data_path = os.path.join(this_file_path, test_data_folder)
        # ------------------------------------------------------------------
        for nmr_data_index in range(len(nmr_datas)):
            test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
            dic, data = ppm_intensity_bruker(test_data)
            pprint(dic)
            pprint(data)

    def test_NmrBruker(self):
        """
        测试NmrBruker。
        """
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_data_folder = "test_data"
        nmr_datas = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', ]
        test_data_path = os.path.join(this_file_path, test_data_folder)
        # ------------------------------------------------------------------
        for nmr_data_index in range(len(nmr_datas)):
            test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
            nmr_obj = NmrBruker(test_data)
            pprint(nmr_obj.data_base_path)
            pprint(nmr_obj.data_path)
            pprint(nmr_obj.pdata_path)
            dic, data = nmr_obj.read_data()
            pprint(dic)
            pprint(data)
            dic, data = nmr_obj.read_pdata()
            pprint(dic)
            pprint(data)
            ppm, intensity = nmr_obj.ppm_intensity()
            pprint(ppm)
            pprint(intensity)

    def test_ppm_intensity_bruker2(self):
        """
        测试ppm_intensity_bruker。
        """
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_data_folder = "test_data"
        nmr_datas = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', ]
        test_data_path = os.path.join(this_file_path, test_data_folder)
        # ------------------------------------------------------------------
        nmr_data_index = 0
        test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
        dic, data = ppm_intensity_bruker(test_data)
        csv_name = "4.csv"
        csv_path = os.path.join(test_data_path, nmr_datas[nmr_data_index],
                                "1", csv_name)
        print(csv_path)
        csv_dic, csv_data = read_txt(csv_path, res_type="ndarrays")
        print(csv_dic)
        print(csv_data)

        print(len(dic))
        print(len(csv_dic))
        print(len(data))
        print(len(csv_data))
        # ------------------------------------------------------------------
        nmr_data_index = 1
        test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
        dic, data = ppm_intensity_bruker(test_data)
        csv_name = "2.csv"
        csv_path = os.path.join(test_data_path, nmr_datas[nmr_data_index],
                                "1", csv_name)
        print(csv_path)
        csv_dic, csv_data = read_txt(csv_path, res_type="ndarrays")
        print(csv_dic)
        print(csv_data)

        print(len(dic))
        print(len(csv_dic))
        print(len(data))
        print(len(csv_data))
        # ------------------------------------------------------------------
        nmr_data_index = 2
        test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
        dic, data = ppm_intensity_bruker(test_data)
        csv_name = "3.csv"
        csv_path = os.path.join(test_data_path, nmr_datas[nmr_data_index],
                                "1", csv_name)
        print(csv_path)
        csv_dic, csv_data = read_txt(csv_path, res_type="ndarrays")
        print(csv_dic)
        print(csv_data)

        print(len(dic))
        print(len(csv_dic))
        print(len(data))
        print(len(csv_data))
        # ------------------------------------------------------------------
        nmr_data_index = 3
        test_data = os.path.join(test_data_path, nmr_datas[nmr_data_index])
        dic, data = ppm_intensity_bruker(test_data)
        print(dic)
        print(data)
        csv_name = "1.csv"
        csv_path = os.path.join(test_data_path, nmr_datas[nmr_data_index],
                                "1", csv_name)
        print(csv_path)
        csv_dic, csv_data = read_txt(csv_path, res_type="ndarrays")
        print(csv_dic)
        print(csv_data)

        print(len(dic))
        print(len(csv_dic))
        print(len(data))
        print(len(csv_data))


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
