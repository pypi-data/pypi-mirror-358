#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_cre_datalyzer.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试cre_datalyzer.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/17     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import math
import os
import re
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from .cre_datalyzer import CreMechDataAnalyzer


# ==================================================================
class TestCreDatalyzer(unittest.TestCase):
    """
    测试cre_datalyzer.py。
    """

    # --------------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        # --------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print("this file name: %s" % this_file_name)
        print("this_file_path: %s" % this_file_path)
        # --------------------------------------------------------
        test_data_path = "test_data"
        test_file_name = "2-3 dry 9.8 15.xlsx"
        test_file = os.path.join(this_file_path, test_data_path, test_file_name)
        print(f"test_file:{test_file}")
        # --------------------------------------------------------
        data = pd.read_excel(test_file, header=0, engine="openpyxl")
        height = float(re.sub(r"[^\d.]", "", data.iat[0, 2]))
        diameter = float(re.sub(r"\D", "", data.iat[0, 3]))
        new_data = data.iloc[1:]

        nos = np.asarray(new_data.iloc[:, 0], dtype=np.int64)
        times = np.asarray(new_data.iloc[:, 1], dtype=np.float64)
        displacements = np.asarray(new_data.iloc[:, 2], dtype=np.float64)
        force = np.asarray(new_data.iloc[:, 3], dtype=np.float64)

        print(f"height:{height},diameter={diameter}")
        print(f"nos:{nos}")
        print(f"times:{times}")
        print(f"displacements:{displacements}")
        print(f"force:{force}")

        # 将字符串转换为Path对象
        path = Path(test_file)
        # 获取文件名
        file_name = path.name
        # 获取文件所在文件夹名
        folder_name = path.parent.name
        # 获取文件所在文件夹的上层文件夹名
        parent_folder_name = (
            path.parent.parent.name if path.parent.parent != Path(".") else "根目录"
        )
        self.analyzer = CreMechDataAnalyzer(
            displacements,
            force,
            times,
            displacement_unit="mm",
            force_unit="N",
            time_unit="min",
            clamp_distance=height,
            clamp_distance_unit="mm",
            cross_area=(math.pi * diameter**2) / 4,
            cross_area_unit="mm^2",
            specimen_name=f"{parent_folder_name}_{folder_name}",
            specimen_no=0,
            raw_file_name=file_name,
        )

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

    def test_init0(self):
        displacements = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        forces = [0.1, 0.2, 0.3, 0.4, 0.42, 0.43, 0.45, 0.46, 0.47, 0.5]
        assert len(displacements) == len(forces)
        times = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.10]
        assert len(times) == len(displacements)
        print("\n\n-----------------------------------------------------")
        cre_datalyzer = CreMechDataAnalyzer(displacements, forces)
        cre_datalyzer.data_logger.print(
            {
                "display.max_columns": None,
                "display.max_rows": None,
                "display.max_colwidth": None,
            }
        )

        this_path = os.path.abspath(os.path.dirname(__file__))
        out_path = os.path.join(this_path, "test_out")
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        csv_file = os.path.join(out_path, "cre_datalyzer.csv")
        print(csv_file)

        cre_datalyzer.data_logger.to_csv(csv_file)
        html_file = os.path.join(out_path, "cre_datalyzer.html")
        cre_datalyzer.data_logger.to_html(html_file)

    def test_init1(self):
        pass



if __name__ == "__main__":
    unittest.main()
