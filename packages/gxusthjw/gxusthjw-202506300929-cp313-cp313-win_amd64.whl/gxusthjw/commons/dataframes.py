#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        dataframes.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      为`pandas.DataFrame`提供辅助方法和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/29     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import (
    Optional, Mapping, Set, FrozenSet, Any, Union, Sequence, Iterable
)

import numpy as np
import pandas as pd

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define helper functions and classes for `pandas.DataFrame`.
"""

__all__ = [
    'create_df_from_item',
    'create_df_from_dict',
    'merge_df',
    'merge_dfs',
    'update_df',
    'updates_df'
]

# 定义 ==============================================================

# 默认的项名称前缀。
__DEFAULT_ITEM_NAME_PREFIX__ = "item"


def create_df_from_item(data: Any, name: Optional[str] = None) -> pd.DataFrame:
    """
    基于指定的数据与数据项名创建pd.DataFrame。

        说明：

            1. 如果参数name不为类型str或None时，抛出异常，
               如果参数name为None，则用“item”代替。

            2. 如果参数data为None，则抛出异常。

            3. 如果参数data是dict, 则利用name从data中取数据（data[name]），
               如果找不到，则使用list(data.values())获取数据。

            4. 如果参数data为标量数据或字符串，则将其封装为列表（[data]），
               标量类型包括：int、float、str、np.generic等。

    :param data: 创建DataFrame的数据。
    :param name: 创建DataFrame的数据项名称。
    :return: 创建得到的DataFrame。
    :rtype: pandas.DataFrame
    """
    # 检查name的类型。
    if not isinstance(name, Union[str, None]):
        raise ValueError("Parameter name must be a str or None.")

    # 获取数据项名称。
    k = name if name is not None else __DEFAULT_ITEM_NAME_PREFIX__

    # 如果是字典，则获取指定的项
    if isinstance(data, Mapping):
        if k in data:
            d = data[k]
        else:
            d = list(data.values())
    else:
        d = data

    # 判断是否为字符串或不可迭代对象
    if isinstance(d, str) or not isinstance(d, Iterable):
        v = np.asarray([d])
    else:
        # 如果是集合类型，先转为列表
        if isinstance(d, (Set, FrozenSet)):
            v = np.asarray(list(d))
        else:
            # 处理其他可迭代对象（如 list, tuple, range, bytes 等）
            try:
                v = np.asarray(d)
            except Exception as e:
                raise ValueError(f"Failed to convert data to numpy array: {e}")

    if v is None or v.ndim != 1:
        raise ValueError("Failed to convert data to one-dimensional numpy array.")

    # 创建DataFrame并返回。
    return pd.DataFrame({k: v})


def create_df_from_dict(data: Mapping[str, Any]) -> pd.DataFrame:
    """
    从指定的字典创建pd.DataFrame。

    :param data: 指定的字典。
    :return: 创建得到的DataFrame。
    :rtype: pandas.DataFrame
    """
    if not isinstance(data, Mapping):
        raise ValueError(f"Expected data of type Mapping, got {type(data).__name__} instead.")
    if not data:
        return pd.DataFrame()
    # 将每个键值对转换为DataFrame，然后合并它们
    dfs = [create_df_from_item(v, k) for k, v in data.items()]
    return merge_dfs(*dfs)


def merge_df(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    合并两个DataFrame。

    如果出现列明重复，则后面相同列名的数据覆盖前面。

    :param df1: 第一个DataFrame。
    :param df2: 第二个DataFrame。
    :return: 合并后的DataFrame。
    :rtype: pandas.DataFrame
    """
    if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
        raise ValueError("Both df1 and df2 must be pandas DataFrames.")
    # 删除df1中与df2相同的列
    df1 = df1.drop(columns=df2.columns, errors="ignore")
    # 使用pd.concat合并两个DataFrame
    merged_df = pd.concat([df1, df2], axis=1)
    return merged_df


def merge_dfs(*dfs):
    """
    合并多个DataFrame对象。

    如果出现列明重复，则后面相同列名的数据覆盖前面。

    :param dfs: 要合并的DataFrame。
    :return: 合并后的DataFrame。
    :rtype: pandas.DataFrame
    """
    if len(dfs) == 0:
        return pd.DataFrame()
    elif len(dfs) == 1:
        return dfs[0]
    elif len(dfs) == 2:
        return merge_df(dfs[0], dfs[1])
    else:
        # 首先合并前两个DataFrame
        merged_df = merge_df(dfs[0], dfs[1])
        # 依次合并剩余的DataFrame
        for df in dfs[2:]:
            merged_df = merge_df(merged_df, df)
        return merged_df


def update_df(df: pd.DataFrame,
              data: Any,
              name: Optional[str] = None) -> pd.DataFrame:
    """
    更新或添加数据项到指定的pd.DataFrame。

        注意：

            1. 如果指定数据项名已经存在，
               则此名所关联的数据将被指定的数据取代。

            2. 如果name为None，则用item_i取代，
               其中i为数据表中数据项的数量。

    :param df: 要被更新的pd.DataFrame。
    :param data: 要更新或添加的数据项数据。
    :param name: 要更新或添加的数据项名。
    :return: 更新或添加后的pd.DataFrame。
    :rtype: pd.DataFrame
    """
    if name is None:
        num_items = df.shape[1]
        name = "{}_{}".format(__DEFAULT_ITEM_NAME_PREFIX__, num_items)

    if not isinstance(name, str):
        raise ValueError(
            "the type of col_name must be a str," "but got {}.".format(name)
        )

    if isinstance(data, Mapping):
        new_df = create_df_from_dict(data)
    elif isinstance(data, pd.DataFrame):
        new_df = data.copy(deep=True)
    else:
        new_df = create_df_from_item(data, name)

    if df is None:
        raise ValueError("df cannot be None.")

    # 判断df是否为空。
    if df.empty:
        res_df = new_df
    else:
        res_df = merge_dfs(df, new_df)

    return res_df


def updates_df(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
    更新或添加数据项到指定的pd.DataFrame。

        1. 对于可选参数args，其作用是指定数据项的数据，args中的每个元素为1条数据项的数据。

            args中每个元素的允许值包括：

            （1）标量值，类型必须为int,float,bool,str或object等。

            （2）类数组值：类型必须为list，tuple，numpy.ndarray,pandas.Series,
                        Iterable, Sequence等。

        2. 对于可选关键字参数kwargs，其作用是指定数据项的名称及其他关键字参数：

            （1）通过item_names关键字参数，如果其为字典（dict），
                则键对应数据项的序号，而值对应数据项名。

            （2）通过item_names关键字参数，如果其为列表（list）或元组（tuple），
                则序号对应数据项的序号，而值对应数据项名。

            （3）如果没有指定item_names关键字参数或者 item_names不符合（1）和（2）的规则，
                则采用缺省的数据项名（item_i的形式）。

            （4）任何数据项名的遗漏，都会以item_i的形式代替。

        3. 对于除item_names外的其他可选关键字参数，将全部按照`键值对`存储。

    :param df: 要被更新的pd.DataFrame。
    :param args: 可选参数，元组类型，用于初始化”数据项“的数据。
    :param kwargs: 可选的关键字参数，字典类型，
                   用于初始化”数据项“的名称及其他属性参数。
    :return: 更新或添加后的pd.DataFrame。
    :rtype: pd.DataFrame
    """
    # 初始数据项数。
    item_count = len(args)

    # 初始数据项名。
    item_names = {}

    # 构建数据项名。
    if "item_names" in kwargs:
        kwargs_item_names = kwargs.pop("item_names")
        if kwargs_item_names is not None:
            # 如果指定数据项名时，使用的是字典。
            if isinstance(kwargs_item_names, Mapping):
                for key in kwargs_item_names.keys():
                    # 字典的键必须是整数，这个整数代表数据项的序号。
                    if not isinstance(key, int):
                        raise ValueError(
                            "the key of item_names must be a int value,"
                            "but got {}".format(key)
                        )
                    # 如果键值超过了初始数据项的数量，则跳过。
                    if key >= item_count:
                        continue
                    key_item_name = kwargs_item_names[key]
                    # 如果字典值类型不是None，则设置为数据项名。
                    if key_item_name is not None:
                        if isinstance(key_item_name, str):
                            item_names[key] = key_item_name
                        else:
                            item_names[key] = str(key_item_name)
                    else:
                        item_names[key] = "{}_{}".format(
                            __DEFAULT_ITEM_NAME_PREFIX__, key
                        )
            # 如果指定数据项名时，使用的是列表或元组。
            elif isinstance(kwargs_item_names, Sequence):
                for item_index in range(len(kwargs_item_names)):
                    if item_index >= item_count:
                        break
                    item_name = kwargs_item_names[item_index]
                    if item_name is not None:
                        if isinstance(item_name, str):
                            item_names[item_index] = item_name
                        else:
                            item_names[item_index] = str(item_name)
                    else:
                        item_names[item_index] = "{}_{}".format(
                            __DEFAULT_ITEM_NAME_PREFIX__, item_index
                        )
            else:
                raise ValueError(
                    "The type of item_names must be one of {{dict,list,tuple}}"
                )
        else:
            current_item_index = df.shape[1]
            for item_index in range(item_count):
                item_names[item_index] = "{}_{}".format(
                    __DEFAULT_ITEM_NAME_PREFIX__, current_item_index + item_index
                )
    else:
        current_item_index = df.shape[1]
        for item_index in range(item_count):
            item_names[item_index] = "{}_{}".format(
                __DEFAULT_ITEM_NAME_PREFIX__, current_item_index + item_index
            )

    new_df = df
    for item_index in range(item_count):
        if item_index in item_names.keys():
            new_df = update_df(new_df, args[item_index], item_names[item_index])
        else:
            new_df = update_df(
                new_df, args[item_index],
                "{}_{}".format(__DEFAULT_ITEM_NAME_PREFIX__, item_index),
            )

    res_df = new_df
    # 其他关键字参数将被转换为对象的属性。
    for key in kwargs.keys():
        res_df = update_df(res_df, kwargs[key], key)

    return res_df
