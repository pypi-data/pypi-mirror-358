#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        benchmark_quasi_sech_cy.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试cython.quasi_sech_cy模块中函数或类的性能。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
# NumPy 基准实现
import numpy as np
import timeit
from typing import Callable

from quasi_sech import sech,quasi_sech
# 导入 Cython 实现
# noinspection PyUnresolvedReferences
from cython import sech_cy_0, quasi_sech_cy
# 定义 ==============================================================


# 测试配置
REPEAT = 100
SIZES = [1_0000,1_00000,1_000000]

def benchmark_func(func: Callable, *args, **kwargs):
    """运行函数并返回平均耗时（秒）"""
    def wrapper():
        with np.errstate(all='ignore'):
            return func(*args, **kwargs)
    duration = timeit.timeit(wrapper, number=REPEAT)
    return duration / REPEAT

def run_benchmark():
    print(f"{'Size':>8} | {'Cython sech_cy':>15} | {'Numpy sech_np':>15} | "
          f"{'Cython quasi_sech_cy':>20} | {'Numpy quasi_sech_np':>20}")
    print("-" * 95)

    for size in SIZES:
        x = np.linspace(-5, 5, size).astype(np.float64)
        peak_width = 2.0
        peak_steepness = 3.0

        cy_sech_time = benchmark_func(sech_cy_0, x)
        py_sech_time = benchmark_func(sech, x)
        cy_qsech_time = benchmark_func(quasi_sech_cy, x, peak_width, peak_steepness)
        py_qsech_time = benchmark_func(quasi_sech, x, peak_width, peak_steepness)

        print(f"{size:8d} | {cy_sech_time:.6f} s/loop | {py_sech_time:.6f} s/loop | "
              f"{cy_qsech_time:.6f} s/loop | {py_qsech_time:.6f} s/loop")

if __name__ == "__main__":
    run_benchmark()