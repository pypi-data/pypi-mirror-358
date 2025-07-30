#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_table.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`数据表`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/28     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
import numpy.typing as npt

import pandas as pd
from typing import (
    Optional, Tuple, Union, Mapping, Sequence
)

from .dataframes import (
    create_df_from_item,
    create_df_from_dict,
    merge_dfs
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents `data table`.
"""

__all__ = [
    'DataTable',
]

# 定义 ==============================================================
# 缺省的数据项名前缀。
__DEFAULT_ITEM_NAME_PREFIX__ = "item_"


class DataTable(object):
    """
    类`DataTable`表征“数据表”。
    """

    def __init__(self, *args, **kwargs):
        """
        类`DataTable`的初始化方法。
        """

        # 初始化数据表中存储数据的对象------------------------------
        # 私有实例变量`__df`用于保存数据表中的数据。
        # 数据表中的数据被保存为pandas.DataFrame格式。
        # 初始化时，数据表为空。
        self.__df = pd.DataFrame()
        # ------------------------------------------------------
        # 将初始化参数更新至数据表中。
        self.updates(*args, **kwargs)
        # 初始化完成 ---------------------------------------------

    def __post_init__(self):
        """
        初始化后的处理方法。

        该方法在对象初始化后调用，用于执行一些额外的初始化操作。
        它不是构造函数的一部分，但补充了构造函数的功能。

        检查实例变量__df是否为None，如果是，则将其初始化为空的DataFrame。
        这样做可能是为了确保__df在对象的生命周期中始终有一个有效的状态，
        即使在初始化时没有被赋予一个值。
        """
        if self.__df is None:
            self.__df = pd.DataFrame()

    @property
    def is_empty(self) -> bool:
        """
        判断数据表是否为空。

        :return: 如果数据表为空，则返回True，否则返回False。
        :rtype: bool
        """
        return self.__df.empty

    @property
    def shape(self) -> Tuple[int, int]:
        """
        获取数据表的形状。

        :return: 元组（行数，列数）。
        :rtype: Tuple[int, int]
        """
        return self.__df.shape

    @property
    def num_items(self) -> int:
        """
        获取数据表中数据项的数量。

        :return: 数据表中数据项的数量。
        :rtype: int
        """
        return self.shape[1]

    def get(self, col_index: Union[str, int]) -> npt.NDArray:
        """
        获取数据表中指定索引的数据项。

        :param col_index: 索引，可以是数据项号或数据项名。
        :return: 数据项。
        """
        if isinstance(col_index, int):
            return np.asarray(self.__df.iloc[:, col_index].dropna())
        else:
            return np.asarray(self.__df[col_index].dropna())

    # -------------------------------------------------------------
    def update(self, data, name: Optional[str] = None):
        """
        更新或添加数据项。

            注意：

                1. 如果数据表中，指定数据项名已经存在，
                   则数据表中此名所关联的数据将被指定的数据取代。

                2. 如果item_name为None，则用item_i取代，
                   其中i为数据表中数据项的数量。

                3. 如果data为dict或pd.DataFrame类型，
                   则name值将被dict的键或pd.DataFrame的列名掩盖。

        :param data: 要更新或添加的数据项数据。
        :param name: 要更新或添加的数据项名。
        """
        if name is None:
            num_items = self.num_items
            name = "{}{}".format(__DEFAULT_ITEM_NAME_PREFIX__, num_items)

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

        # 判断self.__data是否为空。
        if self.__df is None or self.is_empty:
            self.__df = new_df
        else:
            self.__df = merge_dfs(self.__df, new_df)

    def updates(self, *args, **kwargs):
        """
        更新或添加数据。

            1. 对于可选参数args，其作用是指定数据项的数据，args中的每个元素为1条数据项的数据。

                args中每个元素的允许值包括：

                （1）标量值，类型必须为: int,float,bool,str,np.number或object等。

                （2）序列或集（Set)值：类型必须为: list，tuple，numpy.ndarray,pandas.Series,
                            Set, Sequence等。

            2. 对于可选关键字参数kwargs，其作用是指定数据项的名称及其他关键字参数：

                （1）通过`item_names`关键字参数，如果其为字典（dict），
                    则键对应数据项的序号，而值对应数据项名。

                （2）通过`item_names`关键字参数，如果其为列表（list）或元组（tuple），
                    则序号对应数据项的序号，而值对应数据项名。

                （3）如果没有指定`item_names`关键字参数或者 `item_names`不符合（1）和（2）的规则，
                    则采用缺省的数据项名（item_i的形式）。

                （4）任何数据项名的遗漏，都会以item_i的形式代替。

            3. 对于除`item_names`外的其他可选关键字参数，将全部按照`键值对`存储。

        :param args: 可选参数，元组类型，用于初始化”数据项“的数据。
        :param kwargs: 可选的关键字参数，字典类型，
                       用于初始化”数据项“的名称及其他属性参数。
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
                            item_names[key] = "{}{}".format(
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
                            item_names[item_index] = "{}{}".format(
                                __DEFAULT_ITEM_NAME_PREFIX__, item_index
                            )
                else:
                    raise ValueError(
                        "The type of item_names must be one of {{dict,list,tuple}}"
                    )
            else:
                current_item_index = self.shape[1]
                for item_index in range(item_count):
                    item_names[item_index] = "{}{}".format(
                        __DEFAULT_ITEM_NAME_PREFIX__, current_item_index + item_index
                    )
        else:
            current_item_index = self.shape[1]
            for item_index in range(item_count):
                item_names[item_index] = "{}{}".format(
                    __DEFAULT_ITEM_NAME_PREFIX__, current_item_index + item_index
                )

        # 补充遗漏
        for item_index in range(item_count):
            if item_index in item_names.keys():
                self.update(args[item_index], item_names[item_index])
            else:
                self.update(
                    args[item_index],
                    "{}{}".format(__DEFAULT_ITEM_NAME_PREFIX__, item_index),
                )

        # 其他关键字参数将被转换为对象的属性。
        for key in kwargs.keys():
            self.update(kwargs[key], key)

    # ---------------------------------------------------------
    def print(self, options: Optional[dict] = None):
        """
        print数据。

        :param options: 用于设置set_option的键和值。
        """
        if options:
            for key in options.keys():
                pd.set_option(key, options[key])
        print(self.__df)

    # ---------------------------------------------------------

    def to_dataframe(self) -> pd.DataFrame:
        """
        将数据记录器转换为pd.DataFrame。

        :return: 经转换得到的pd.DataFrame。
        """
        return self.__df.copy(deep=True)

    def to_csv(self, *args, **kwargs):
        """
        数据输出至csv格式文件。

        :param args: pandas.to_csv方法所需的可选参数。
        :param kwargs: pandas.to_csv方法所需的可选关键字参数。
        :return: pandas.to_csv方法的返回值。
        """
        return self.__df.to_csv(*args, **kwargs)

    def to_excel(self, excel_writer, *args, **kwargs):
        """
        数据输出至excel格式文件。

        :param excel_writer: path-like, file-like, or ExcelWriter object
            File path or existing ExcelWriter.
        :param args: pandas.to_excel方法所需的可选参数。
        :param kwargs: pandas.to_excel方法所需的可选关键字参数。
        """
        self.__df.to_excel(excel_writer, *args, **kwargs)

    def to_dict(self, *args, **kwargs):
        """
        数据转换为dict.

        :param args: pandas.to_dict方法所需的可选参数。
        :param kwargs:pandas.to_dict方法所需的可选关键字参数。
        :return: dict对象。
        """
        return self.__df.to_dict(*args, **kwargs)

    def to_json(self, *args, **kwargs):
        """
        数据转换为json字符串。

        :param args: pandas.to_json方法所需的可选参数。
        :param kwargs:pandas.to_json方法所需的可选关键字参数。
        :return: json字符串。
        """
        return self.__df.to_json(*args, **kwargs)

    def to_latex(self, *args, **kwargs):
        """
        数据转换为latex字符串。

        :param args: pandas.to_latex方法所需的可选参数。
        :param kwargs:pandas.to_latex方法所需的可选关键字参数。
        :return: latex字符串。
        """
        return self.__df.to_latex(*args, **kwargs)

    def to_markdown(self, *args, **kwargs):
        """
        数据转换为markdown字符串。

        :param args: pandas.to_markdown方法所需的可选参数。
        :param kwargs:pandas.to_markdown方法所需的可选关键字参数。
        :return: markdown字符串。
        """
        return self.__df.to_markdown(*args, **kwargs)

    def to_string(self, *args, **kwargs):
        """
        数据转换为字符串。

        :param args: pandas.to_string方法所需的可选参数。
        :param kwargs:pandas.to_string方法所需的可选关键字参数。
        :return: 字符串。
        """
        return self.__df.to_string(*args, **kwargs)

    def to_html(self, *args, **kwargs):
        """
        数据转换为html字符串。

        :param args: pandas.to_html方法所需的可选参数。
        :param kwargs:pandas.to_html方法所需的可选关键字参数。
        :return: html字符串。
        """
        return self.__df.to_html(*args, **kwargs)

    def to_clipboard(self, *args, **kwargs):
        """
        数据复制到剪切板。

        :param args: pandas.to_clipboard方法所需的可选参数。
        :param kwargs:pandas.to_clipboard方法所需的可选关键字参数。
        """
        self.__df.to_clipboard(*args, **kwargs)

    # ---------------------------------------------------
    @staticmethod
    def from_dict(data_dict, *args, **kwargs):
        """
        从数据字典构建数据记录器。

        :param data_dict: 数据字典。
        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.DataFrame.from_dict(data_dict, *args, **kwargs)
        data_table = DataTable()
        data_table.update(data)
        return data_table

    @staticmethod
    def from_csv(file, *args, **kwargs):
        """
        从csv文件构建数据记录器。

        :param file: csv文件。
        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.read_csv(file, *args, **kwargs)
        data_table = DataTable()
        data_table.update(data)
        return data_table

    @staticmethod
    def from_excel(file, *args, **kwargs):
        """
        从excel文件构建数据记录器。

        :param file: excel文件。
        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.read_excel(file, *args, **kwargs)
        data_table = DataTable()
        data_table.update(data)
        return data_table

    @staticmethod
    def from_table(file, *args, **kwargs):
        """
        从文本文件构建数据记录器。

        :param file: 文本文件。
        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.read_table(file, *args, **kwargs)
        data_table = DataTable()
        data_table.update(data)
        return data_table

    @staticmethod
    def from_json(file, *args, **kwargs):
        """
        从json文件构建数据记录器。

        :param file: json文件。
        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.read_json(file, *args, **kwargs)
        data_table = DataTable()
        data_table.update(data)
        return data_table

    @staticmethod
    def from_html(file, *args, **kwargs):
        """
        从html文件构建数据记录器。

        :param file: html文件。
        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.read_html(file, *args, **kwargs)
        data_table = DataTable()
        for di in data:
            data_table.update(di)
        return data_table

    @staticmethod
    def from_clipboard(*args, **kwargs):
        """
        从系统剪贴板构建数据记录器。

        :param args: 可选位置参数。
        :param kwargs: 可选关键字参数。
        :return:数据记录器。
        :rtype: DataTable
        """
        data = pd.read_clipboard(*args, **kwargs)
        data_table = DataTable()
        data_table.update(data)
        return data_table

# ================================================================
