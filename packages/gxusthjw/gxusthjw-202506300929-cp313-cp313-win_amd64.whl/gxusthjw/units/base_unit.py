#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        base_unit.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`计量单位`基类”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/10/02     revise
#       Jiwei Huang        0.0.1         2024/09/21     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from abc import ABC, abstractmethod

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a base class that represents `measuring unit`.
"""

__all__ = [
    'Unit'
]


# 定义 ================================================================

class Unit(ABC):
    """
    类`Unit`表征"计量单位"，是所有"计量单位"类的父类。
    """

    @property
    def name(self) -> str:
        """
        计量单位的名字。

            约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: str
        """
        # 获取当前实例所属的类名
        return self.__class__.__name__

    @property
    @abstractmethod
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def family(self) -> str:
        """
        计量单位所隶属的单位族。

        每个计量单位均隶属于某一单位族，例如：

            “米”、“分米”、“厘米”等都隶属于”长度单位“；

            "克“、”毫克“、”微克“等都隶属于”重量单位”；

            ”小时“、"秒"、”分“等都隶属于”时间单位”。

        同族的单位间可相互转换，非同族的单位间不可相互转换，
        强制执行非同族单位间的转换将触发`ValueError`类型的异常。

        :return: 计量单位所隶属的单位族。
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def benchmark_unit(self):
        """
        计量单位所属单位族的基准单位。

        每个计量单位族，有且只有一个基准单位（Benchmark unit），

        例如：

            ”长度单位”的基准单位为”米“。

            ”重量单位”的基准单位为”克“。

        :return: 计量单位所属单位族的基准单位。
        :rtype: Unit
        """
        pass

    @property
    @abstractmethod
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子，例如：

            （1）长度单位的基准单位为”米“，而 1 厘米 = 0.01 米，
                则 ”厘米“的转换因子即为0.01。

            （2）重量单位的基准单位为“克”，而 1 千克 = 1000 克，
                 则“千克”的转换因子即为1000.0。

        由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子，例如：

            （1）长度单位的基准单位为”米“，而 1 米 = 100 厘米，
                则 ”厘米“的逆转换因子即为100。

            （2）重量单位的基准单位为“克”，而 1 克 = 0.001 千克，
                则“千克”的逆转换因子即为0.001。

        由此定义可知：1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，
                 则返回True，否则返回False。
        :rtype: bool
        """
        pass

    @property
    @abstractmethod
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，
                 则返回True，否则返回False。
        :rtype: bool
        """
        pass

    def is_compatible(self, unit) -> bool:
        """
        判断此单位与指定单位是否兼容。

        如果此单位与指定单位隶属同一单位族，则返回True，否则返回False。

        :param unit: 指定单位。
        :type unit: Unit
        :return: 如果此单位与指定单位隶属同一单位族，
                 则返回True，否则返回False。
        :rtype: bool
        """
        return Unit.is_compatible_between(self, unit)

    def convert_to_benchmark(self, value: float) -> float:
        """
        将带有此单位的值转换为带有基准单位的值。

        :param value: 带有此单位的值。
        :type value: float
        :return: 带有基准单位的值。
        :rtype: float
        """
        return value * self.cfactor

    def convert_from_benchmark(self, value: float) -> float:
        """
        将带有基准单位的值转换为带有此单位的值。

        :param value: 带有基准单位的值。
        :type value: float
        :return: 带有此单位的值。
        :rtype: float
        """
        return value * self.rcfactor

    def cfactor_to(self, unit) -> float:
        """
        此单位与指定单位间的转换因子，例如：

            （1）设此单位为”米“，指定单位为：“厘米”，而 1 米 = 100 厘米，
                则转换因子即为100。

            （2）设此单位为“克”，指定单位为：“千克”，而 1 克 = 0.001 千克，
                 则转换因子即为0.001。

        由此定义可知：1 此单位 = cfactor_to(unit) 指定单位。

        :param unit: 指定单位。
        :type unit: Unit
        :return: 转换因子（此单位与指定单位间）。
        :rtype: float
        :raise ValueError: 当指定的新单位与此单位不兼容时，抛出此异常。
        """
        return self.convert(1.0, unit)

    def rcfactor_to(self, unit) -> float:
        """
        此单位与指定单位间的逆转换因子，例如：

            （1）设此单位为”米“，指定单位为：“厘米”，而 1 厘米 = 0.01 米，
                则逆转换因子即为0.01。

            （2）设此单位为“克”，指定单位为：“千克”，而 1 千克 = 1000 克，
                 则逆转换因子即为1000.0。

        由此定义可知：1 指定单位 = rcfactor_to(unit) 此单位。

        :param unit: 指定单位。
        :type unit: Unit
        :return: 逆转换因子（此单位与指定单位间）。
        :rtype: float
        :raise ValueError: 当指定的新单位与此单位不兼容时，抛出此异常。
        """
        return unit.convert(1.0, self)

    def convert(self, value, new_unit) -> float:
        """
        将带有此单位的值转换为带有指定单位的新值。

        :param value: 带有此单位的值。
        :type value: float
        :param new_unit: 指定的新单位。
        :type new_unit: Unit
        :return: 带有指定新单位的新值。
        :rtype: float
        :raise ValueError: 当指定的新单位与此单位不兼容时，抛出此异常。
        """
        if Unit.is_compatible_between(self, new_unit):
            return new_unit.convert_from_benchmark(
                self.convert_to_benchmark(value))
        raise ValueError("The conversion cannot be performed from %s to %s, " +
                         "because they belong to different unit families " +
                         "(%s belong to %s and %s belong to %s)." % self.name,
                         new_unit.name, self.name, self.family, new_unit.name,
                         new_unit.family)

    @staticmethod
    def is_compatible_between(unit1, unit2) -> bool:
        """
        判断两个单位是否兼容。
        如果两个单位隶属同一单位族，则返回True，否则返回False。

        :param unit1: 要对比的单位1。
        :type unit1: Unit
        :param unit2: 要对比的单位2。
        :type unit2: Unit
        :return: 如果两个单位隶属同一单位族，则返回True，否则返回False。
        :rtype: bool
        """
        return unit1.family == unit2.family

    def __str__(self):
        """
        重载：对象字符串。

        :return: 对象字符串。
        """
        return "%s" % self.name

    def __repr__(self):
        """
        重载：对象字符串。

        :return: 对象字符串。
        """
        return "%s" % self.name

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: bool
        """
        if self is other:
            return True
        elif not isinstance(other, Unit):
            return False
        else:
            return self.name == other.name and \
                self.symbol == other.symbol and \
                self.description == other.description and \
                self.family == other.family

    def __ne__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的不相等性。

        :param other: 另一个对象。
        :return: 不相等返回True，否则返回False。
        :rtype: bool
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: int
        """
        return hash((self.name,
                     self.symbol,
                     self.description,
                     self.family))
# ===============================================================
