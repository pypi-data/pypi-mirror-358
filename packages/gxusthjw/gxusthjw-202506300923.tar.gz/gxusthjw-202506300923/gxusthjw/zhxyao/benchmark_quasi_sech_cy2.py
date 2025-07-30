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
from typing import Callable, Any

from quasi_sech import sech, sech_np

# 导入 Cython 实现
# noinspection PyUnresolvedReferences
from cython import sech_cy, sech_cy_0, quasi_sech_cy


# 定义 ==============================================================
# noinspection PyBroadException
def benchmark_func(func: Callable[..., Any],
                   repeat: int, *args, **kwargs):
    """
    对给定函数执行性能基准测试，返回平均执行时间（单位：秒）

    :param func: 要测试的函数。
    :param repeat: 执行次数。
    :param args: func 的位置参数。
    :param kwargs: 可选关键字参数，其中，
                   1. 'use_np_errstate'用于支持控制 NumPy 错误状态；
                   2. 'use_try'用于指示是否采用try语句截收函数执行的异常。
                   3. 其余关键字参数全部传给func，作为func 的关键字参数。
    :return: 平均单次执行时间（秒）。
    """
    use_np_errstate: bool = kwargs.pop('use_np_errstate', False)
    use_try: bool = kwargs.pop('use_try', False)

    def wrapper():
        if use_np_errstate:
            with np.errstate(all='ignore'):
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    if use_try:
        try:
            duration = timeit.timeit(wrapper, number=repeat)
            return duration / repeat
        except Exception:
            return float('inf')  # 返回无穷大表示无效结果
    else:
        duration = timeit.timeit(wrapper, number=repeat)
        return duration / repeat

def run_benchmark():
    print(f"{'Size':>8} | {'sech':>10} | {'sech_np':>8} | "
          f"{'sech_cy':>8} | {'sech_cy_0':>8} | ")
    print("-" * 65)
    sizes = [1_000, 10000, 100000, 1000000]
    times = 100
    for size in sizes:
        x = np.linspace(-5, 5, size).astype(np.float64)

        sech_time = benchmark_func(sech, times, x)
        np_sech_time = benchmark_func(sech_np, times, x)
        cy_sech_time = benchmark_func(sech_cy, times, x)
        cy0_sech_time = benchmark_func(sech_cy_0, times, x)

        print(f"{size:8d} | {sech_time:.6f} s | {np_sech_time / sech_time:.6f} | "
              f"{cy_sech_time / sech_time:.6f} | {cy_sech_time / cy0_sech_time:.6f}  |")


if __name__ == "__main__":
    run_benchmark()
