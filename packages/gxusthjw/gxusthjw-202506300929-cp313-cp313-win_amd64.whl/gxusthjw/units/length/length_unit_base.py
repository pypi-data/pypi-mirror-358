#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        length_unit_base.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`长度单位`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/09/30     revise
#       Jiwei Huang        0.0.1         2024/09/14     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import threading
from abc import ABC
from typing import override

from ..base_unit import Unit

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining classes that represents `length unit`.
"""

__all__ = [
    'LengthUnit',
    'MetricLengthUnit',
    'Kilometer',
    'Meter',
    'Decimeter',
    'Centimeter',
    'Millimeter',
    'Micrometer',
    'Nanometer',
    'Picometer',
    'Angstrom',
    'km',
    'm',
    'dm',
    'cm',
    'mm',
    'µm',
    'nm',
    'pm',
    'Å'
]


# 定义 ===============================================================
class LengthUnit(Unit, ABC):
    """
    类`LengthUnit`表征“长度单位”。
    """

    @override
    @property
    def family(self) -> str:
        """
        长度单位所隶属的单位族。

        :return: "LengthUnit"。
        """
        return "LengthUnit"

    @override
    @property
    def benchmark_unit(self):
        """
        长度单位的基准单位为“米”。

        :return: 长度单位的基准单位“米”。
        """
        return Meter()


# =============================================================================
# -----------------------------------------------------------------------------
# 可识别的Kilometer字符串。
_recognizable_kilometer_unit_str = ["km", "kilometer", "Kilometer", "KiloMeter"]

# 可识别的Meter字符串。
_recognizable_meter_unit_str = ["m", "meter", "Meter"]

# 可识别的Decimeter字符串。
_recognizable_decimeter_unit_str = ["dm", "decimeter", "Decimeter", "DeciMeter"]

# 可识别的Centimeter字符串。
_recognizable_centimeter_unit_str = ["cm", "centimeter", "Centimeter", "CentiMeter"]

# 可识别的Millimeter字符串。
_recognizable_millimeter_unit_str = ["mm", "millimeter", "Millimeter", "MilliMeter"]

# 可识别的Micrometer字符串。
_recognizable_micrometer_unit_str = ["μm", "micrometer", "Micrometer", "MicroMeter"]

# 可识别的Nanometer字符串。
_recognizable_nanometer_unit_str = ["nm", "nanometer", "Nanometer", "NanoMeter"]

# 可识别的Picometer字符串。
_recognizable_picometer_unit_str = ["pm", "picometer", "Picometer", "PicoMeter"]

# 可识别的Angstrom字符串。
_recognizable_angstrom_unit_str = ["angstrom", "Angstrom", "A", "Å"]


# -----------------------------------------------------------------------------

class MetricLengthUnit(LengthUnit, ABC):
    """
    类`MetricLengthUnit`表征`公制长度单位`。
    """
    pass


# -----------------------------------------------------------------------------
class Kilometer(MetricLengthUnit):
    """
    类`Kilometer`表征“千米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()

    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Kilometer"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "km"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 km = 1000 m."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1000

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 0.001

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Kilometer):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_kilometer_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
km = Kilometer()


# -----------------------------------------------------------------------

class Meter(MetricLengthUnit):
    """
    类`Meter`表征“米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()

    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Meter"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "m"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 meter."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Meter):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_meter_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
m = Kilometer()


# -----------------------------------------------------------------------


class Decimeter(MetricLengthUnit):
    """
    类`Decimeter`表征“分米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()

    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Decimeter"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "dm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 dm = 0.1 m"

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 0.1

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 10

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Decimeter):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_decimeter_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
dm = Decimeter()


# -----------------------------------------------------------------------


class Centimeter(MetricLengthUnit):
    """
    类`Centimeter`表征“厘米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Centimeter"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "cm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 cm = 0.01 m"

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 0.01

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 100

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Centimeter):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_centimeter_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
cm = Centimeter()


# -----------------------------------------------------------------------


class Millimeter(MetricLengthUnit):
    """
    类`Millimeter`表征“毫米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Millimeter"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "mm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 mm = 0.001 m."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 0.001

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1000

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Millimeter):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_millimeter_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
mm = Millimeter()


# -----------------------------------------------------------------------


class Micrometer(MetricLengthUnit):
    """
    类`Micrometer`表征“微米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Micrometer"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "µm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 µm = 1e-6 m"

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1e-6

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1e6

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Micrometer):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_micrometer_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
# noinspection NonAsciiCharacters
µm = Micrometer()


# -----------------------------------------------------------------------


class Nanometer(MetricLengthUnit):
    """
    类`Nanometer`表征“纳米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Nanometer"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "nm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 nm = 1e-9 m"

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1e-9

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1e9

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Nanometer):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_nanometer_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
nm = Nanometer()


# -----------------------------------------------------------------------


class Picometer(MetricLengthUnit):
    """
    类`Picometer`表征“皮米”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Picometer"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "pm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 pm = 1e-12 m"

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1e-12

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1e12

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Picometer):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_picometer_unit_str:
            return Kilometer()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
pm = Picometer()


# -----------------------------------------------------------------------


class Angstrom(MetricLengthUnit):
    """
    类`Angstrom`表征“埃”。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================

    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Angstrom"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "Å"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 Å = 1.0e-10 meter"

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子。

            由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1.0e-10

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子。

            1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1.0e10

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Angstrom):
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
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Kilometer对象。

        :param unit_str: 线密度字符串。
        :return: Kilometer对象。
        """
        if unit_str in _recognizable_angstrom_unit_str:
            return Angstrom()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
# noinspection NonAsciiCharacters
Å = Angstrom()

# -----------------------------------------------------------------------
# =======================================================================
