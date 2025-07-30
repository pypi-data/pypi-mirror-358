#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_deriv_quasi_sech.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试deriv_quasi_sech.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
import unittest

import numpy as np

from ..commons import (
    read_txt
)

from .quasi_sech import (
    quasi_sech
)

from .deriv_quasi_sech import (
    quasi_sech_ifft
)

from .deriv_quasi_sech_fp import (
    quasi_sech_ifft_fp
)
# 定义 ==============================================================
class TestDerivQuasiSech(unittest.TestCase):
    """
    测试deriv_quasi_sech.py。
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

    def test_quasi_sech(self):
        r = np.linspace(0, 20, 200001,
                        endpoint=True, dtype=np.float64)
        qs = quasi_sech(r, 246, 2)
        _, igg1, _ = quasi_sech_ifft(246, 2)
        _, igg2, _ = quasi_sech_ifft_fp(246, 2)

        print(qs)
        print(igg1)
        print(igg2)

    def test_quasi_sech_ifft_zhxyao(self):
        tc1, igg1, r_values1 = quasi_sech_ifft(246, 2)
        tc2, igg2, r_values2 = quasi_sech_ifft(246, 2)
        self.assertTrue(np.allclose(tc1, tc2, rtol=0, atol=0))
        self.assertTrue(np.allclose(igg1, igg2, rtol=0, atol=0))
        self.assertTrue(np.allclose(r_values1, r_values2, rtol=0, atol=0))

        this_path = os.path.abspath(os.path.dirname(__file__))
        mat_path = os.path.join(this_path, "matlab_zhxyao")
        data_file = os.path.join(mat_path, "Sechpf.csv")
        mat_data = read_txt(data_file, sep=',', skiprows=1,
                            cols={0: "res_246_2", 1: "res_1246_2", 2: "res_200_5"},
                            res_type='dataframe')

        res0, _, _ = quasi_sech_ifft(246, 2)
        res1, _, _ = quasi_sech_ifft(1246, 2)
        res2, _, _ = quasi_sech_ifft(200, 5)

        res0_a, _, _ = quasi_sech_ifft(246, 2)
        res1_a, _, _ = quasi_sech_ifft(1246, 2)
        res2_a, _, _ = quasi_sech_ifft(200, 5)

        print(np.array(mat_data["res_246_2"]))
        print(res0)
        print(res0_a)
        self.assertTrue(np.allclose(np.array(mat_data["res_246_2"]), res0, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(np.array(mat_data["res_246_2"]), res0_a, rtol=0, atol=1e-15))
        print(len(np.array(mat_data["res_246_2"])))
        print(len(res0))
        print(len(res0_a))

        print(np.array(mat_data["res_1246_2"]))
        print(res1)
        print(res1_a)
        self.assertTrue(np.allclose(np.array(mat_data["res_1246_2"]), res1, rtol=0, atol=1e-12))
        self.assertTrue(np.allclose(np.array(mat_data["res_1246_2"]), res1_a, rtol=0, atol=1e-12))
        print(len(np.array(mat_data["res_1246_2"])))
        print(len(res1))
        print(len(res1_a))

        print(np.array(mat_data["res_200_5"]))
        print(res2)
        print(res2_a)
        self.assertTrue(np.allclose(np.array(mat_data["res_200_5"]), res2, rtol=0, atol=1e-12))
        self.assertTrue(np.allclose(np.array(mat_data["res_200_5"]), res2_a, rtol=0, atol=1e-12))
        print(len(np.array(mat_data["res_200_5"])))
        print(len(res2))
        print(len(res2_a))

# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
