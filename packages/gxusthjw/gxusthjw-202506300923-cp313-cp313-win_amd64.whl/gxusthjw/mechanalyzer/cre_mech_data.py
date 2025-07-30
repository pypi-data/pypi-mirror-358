#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        cre_mech_data.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与`恒（常）应变速率力学数据及其分析`相关的方法和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/29     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import copy
from typing import Optional
import numpy as np
import numpy.typing as npt
from ..fitters import interactive_linear_fitting_sm
from .mech_data import (
    MechanicalData,
)
from ..commons import (
    NumberSequence,
    to_number_1darray,
)

from .unit_convert import (
    length_unit_to_mm,
    time_unit_to_s,
    force_unit_to_cn,
    area_unit_to_mm2,
    speed_unit_to_mms,
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define functions and classes related to 
`constant strain rate mechanical data and its analysis`.
"""

__all__ = [
    'CreMechanicalData'
]


# 定义 ==============================================================

class CreMechanicalData(MechanicalData):
    """
    类`CreMechanicalData`表征“恒（常）应变速率力学数据”。

        力学试验仪按照加载方式的不同，可分为三种基本类型：

        (1) 等速伸长型（Constant Rate of Extension, CRE）:
            试样以恒定的速度被拉伸，直到断裂。主要特点是伸长量与时间成正比。
            由于拉伸过程中，试样的应变率不变，故又称为恒（常）应变速率（Constant Strain Rate, CSR）型力学测试。

        (2)等加负荷型(Constant Rate of Loading, CRL):
           与等速伸长型（CRE）相比，在CRL测试中，试验机以恒定的速率增加施加于试样的载荷，
           而不是以恒定的速度拉伸试样。主要的特点是受力的大小与时间成正比。

        (3)等速牵引型(Constant Rate of Traverse, CRT)：
            等速牵引型强力机的主要代表是摆锤式强力仪，其发展比较早，也比较成熟，目前仍大量应用。
            例如,测棉花束纤维强力的斯特洛强力仪，其主要特点是牵引部件（夹持器）的位移与时间成正比，
            由此定义可知，CRT与CRE的原理是一致的。

        目前很多标准规定或推荐采用CRE型力学试验仪。
    """

    def __init__(
            self,
            displacements: NumberSequence,
            forces: NumberSequence,
            times: Optional[NumberSequence] = None,
            *,
            displacement_unit: str = "mm",
            force_unit: str = "cN",
            time_unit: str = "s",
            clamp_distance: Optional[float] = None,
            clamp_distance_unit: str = "mm",
            cross_area: Optional[float] = None,
            cross_area_unit: str = "mm^2",
            speed: Optional[float] = None,
            speed_unit: str = "mm/s",
            sampling_frequency: Optional[float] = None,
            sampling_frequency_unit: str = "Hz",
            **kwargs,
    ):
        """
        类`CreMechanicalData`的初始化方法。

        :param displacements: 位移数据项。
        :param forces: 力数据项。
        :param times: 时间数据项，默认值为：None。
        :param displacement_unit: 位移数据的单位，缺省值为：mm。
        :param force_unit: 力数据的单位，缺省值为：cN。
        :param time_unit: 时间数据的单位，缺省值为：s。
        :param clamp_distance: 夹持距离，缺省值为：None。
        :param clamp_distance_unit: 夹持距离的单位，缺省值为：mm。
        :param cross_area: 截面积，缺省值为：None。
        :param cross_area_unit: 截面积的单位，缺省值为：mm^2。
        :param speed: 拉伸或压缩速度，缺省值为：None。
        :param speed_unit: 拉伸或压缩速度的单位，缺省值为：mm/s。
        :param sampling_frequency: 采样频率。单位：Hz，即，次/s。
        :param sampling_frequency_unit: 采样频率的单位，缺省值为：Hz，即：次/s。
        :param kwargs: 其他可选关键字参数。
        """
        # 数据初始化 ----------------------------------------------------
        if displacements is None:
            raise ValueError("Expect displacements to be not None.")
        self.__displacements = to_number_1darray(displacements)
        if forces is None:
            raise ValueError("Expect forces to be not None.")
        self.__forces = to_number_1darray(forces)
        self.__times = to_number_1darray(times) if times is not None else None
        # -------------------------------------------------------------
        # 蕴含数据 ------------------------------------------------------
        self.__data_len = self.__displacements.shape[0]

        # 要求各数据项的长度相同。
        if self.__forces.shape[0] != self.__data_len:
            raise ValueError(
                "Expect data items (displacements,forces)" " to be the same length."
            )

        if self.__times is not None and self.__times.shape[0] != self.__data_len:
            raise ValueError(
                "Expect data items (displacements,times)" " to be the same length."
            )

        # 初始化编号数据项。
        self.__data_nos = np.arange(1, self.__data_len + 1)
        # 设置编号数据项为不可变。
        self.__data_nos.setflags(write=False)
        # -------------------------------------------------------------
        # 单位转换 -----------------------------------------------------
        if displacement_unit not in ["m", "dm", "cm", "mm"]:
            raise ValueError(
                "Expect displacement_unit to be 'm' or 'dm' or 'cm' or 'mm'."
            )
        self.__displacements = length_unit_to_mm(
            self.__displacements, displacement_unit
        )
        self.__displacements.setflags(write=False)
        self.__displacement_unit = "mm"

        if force_unit not in ["N", "cN"]:
            raise ValueError("Expect force_unit to be 'N', 'cN'.")
        self.__forces = force_unit_to_cn(self.__forces, force_unit)
        self.__forces.setflags(write=False)
        self.__force_unit = "cN"

        if time_unit not in ["h", "min", "s"]:
            raise ValueError("Expect time_unit to be 'h' or 'min' or 's'.")
        if self.__times is not None:
            self.__times = time_unit_to_s(self.__times, time_unit)
            self.__times.setflags(write=False)
        self.__time_unit = "s"
        # --------------------------------------------------------------
        # 初始化其他参数 --------------------------------------------------
        if clamp_distance is not None and clamp_distance <= 0:
            raise ValueError("Expect clamp_distance to be greater than 0.")
        else:
            self.__clamp_distance = clamp_distance

        if clamp_distance_unit not in ["m", "dm", "cm", "mm"]:
            raise ValueError(
                "Expect clamp_distance_unit to be 'm' or 'dm' or 'cm' or 'mm'."
            )
        if self.__clamp_distance is not None:
            self.__clamp_distance = length_unit_to_mm(
                self.__clamp_distance, clamp_distance_unit
            )
        self.__clamp_distance_unit = "mm"

        if cross_area is not None and cross_area <= 0:
            raise ValueError("Expect cross_area to be greater than 0.")
        else:
            self.__cross_area = cross_area

        if cross_area_unit not in ["m^2", "dm^2", "cm^2", "mm^2"]:
            raise ValueError(
                "Expect cross_area_unit to be 'm^2' or 'dm^2' or 'cm^2' or 'mm^2'."
            )
        if self.__cross_area is not None:
            self.__cross_area = area_unit_to_mm2(self.__cross_area, cross_area_unit)
        self.__cross_area_unit = "mm^2"

        if speed is not None and speed <= 0:
            raise ValueError("Expect speed to be greater than 0.")
        else:
            self.__speed = speed

        if speed_unit not in [
            "m/h",
            "dm/h",
            "cm/h",
            "mm/h",
            "m/min",
            "dm/min",
            "cm/min",
            "mm/min",
            "m/s",
            "dm/s",
            "cm/s",
            "mm/s",
        ]:
            raise ValueError(
                "Expect speed_unit to be "
                "'m/h' or 'dm/h' or 'cm/h' or 'mm/h' or "
                "'m/min' or 'dm/min' or 'cm/min' or 'mm/min' or "
                "'m/s' or 'dm/s' or 'cm/s' or 'mm/s'."
            )

        if self.__speed is not None:
            self.__speed = speed_unit_to_mms(self.__speed, speed_unit)
        self.__speed_unit = "mm/s"

        if sampling_frequency is not None and sampling_frequency <= 0:
            raise ValueError("Expect sampling_frequency to be greater than 0.")
        else:
            self.__sampling_frequency = sampling_frequency
        # 采样频率的单位只支持Hz，即：次/每秒。
        if sampling_frequency_unit not in ["Hz", "times/s"]:
            raise ValueError("Expect sampling_frequency_unit to be 'Hz' and 'times/s'.")
        self.__sampling_frequency_unit = "Hz"
        # --------------------------------------------------------------
        super(CreMechanicalData, self).__init__(
            **kwargs
        )
        # 记录数据 -------------------------------------------------------
        self.data_logger.log(self.__displacements, "displacements")
        self.data_logger.log(self.__displacement_unit, "displacement_unit")
        self.data_logger.log(self.__forces, "forces")
        self.data_logger.log(self.__force_unit, "force_unit")

        self.data_logger.log(self.__times, "times")
        self.data_logger.log(self.__time_unit, "time_unit")

        self.data_logger.log(self.__data_nos, "data_nos")
        self.data_logger.log(self.__data_len, "data_len")

        self.data_logger.log(self.__clamp_distance, "clamp_distance")
        self.data_logger.log(self.__clamp_distance_unit, "clamp_distance_unit")

        self.data_logger.log(self.__cross_area, "cross_area")
        self.data_logger.log(self.__cross_area_unit, "cross_area_unit")

        self.data_logger.log(self.__speed, "speed")
        self.data_logger.log(self.__speed_unit, "speed_unit")

        self.data_logger.log(self.__sampling_frequency, "sampling_frequency")
        self.data_logger.log(self.__sampling_frequency_unit, "sampling_frequency_unit")
        # ---------------------------------------------------------------------
        self.__kwargs = kwargs
        # init 结束 ------------------------------------------------------------

    # ===================================================================
    # noinspection PyTypeChecker
    @property
    def displacements(self) -> npt.NDArray[np.float64]:
        """
        获取位移数据项。

        :return: 位移数据项。
        """
        return self.__displacements

    @property
    def displacement_unit(self) -> str:
        """
        获取位移数据项的单位。

            位移数据项的单位必须为：`mm`。

        :return: 位移数据项的单位。
        """
        return self.__displacement_unit

    # noinspection PyTypeChecker
    @property
    def forces(self) -> npt.NDArray[np.float64]:
        """
        获取力数据项。

        :return: 力数据项。
        """
        return self.__forces

    @property
    def force_unit(self) -> str:
        """
        获取力数据项的单位。

            力数据项的单位必须为：`cN`。

        :return: 力数据项的单位。
        """
        return self.__force_unit

    # noinspection PyTypeChecker
    @property
    def times(self) -> Optional[npt.NDArray[np.float64]]:
        """
        获取时间数据项。

        :return: 时间数据项。
        """
        return self.__times

    @property
    def time_unit(self) -> Optional[str]:
        """
        获取时间数据项的单位。

            时间数据项的单位必须为：`s`。

        :return: 时间数据项的单位。
        """
        return self.__time_unit

    def set_times(self, times: NumberSequence, time_unit: str = "s"):
        """
        设置时间数据项。

        :param times: 时间数据项的数据。
        :param time_unit: 时间数据项的单位。
        :return: None
        """
        self.__times = to_number_1darray(times) if times is not None else None
        if time_unit not in ["h", "min", "s"]:
            raise ValueError("Expect time_unit to be 'h' or 'min' or 's'.")
        if self.__times is not None:
            self.__times = time_unit_to_s(self.__times, time_unit)
            self.__times.setflags(write=False)
        self.__time_unit = "s"
        self.data_logger.log(self.__times, "times")
        self.data_logger.log(self.__time_unit, "time_unit")

    @property
    def data_len(self) -> int:
        """
        获取数据长度。

        :return: 数据长度。
        """
        return self.__data_len

    @property
    def data_nos(self) -> npt.NDArray[np.int_]:
        """
        获取编号数据项。

        :return: 编号数据项。
        """
        return self.__data_nos

    @property
    def clamp_distance(self) -> Optional[float]:
        """
        获取夹持距离。

        :return: 夹持距离。
        """
        return self.__clamp_distance

    @property
    def clamp_distance_unit(self) -> Optional[str]:
        """
        获取夹持距离的单位。

        :return: 夹持距离的单位。
        """
        return self.__clamp_distance_unit

    def set_clamp_distance(self, clamp_distance: float, clamp_distance_unit: str = "mm"):
        """
        设置夹持距离。

        :param clamp_distance: 夹持距离的值。
        :param clamp_distance_unit: 夹持距离的单位。
        """
        if clamp_distance is not None and clamp_distance <= 0:
            raise ValueError("Expect clamp_distance to be greater than 0.")
        else:
            self.__clamp_distance = clamp_distance

        if clamp_distance_unit not in ["m", "dm", "cm", "mm"]:
            raise ValueError(
                "Expect clamp_distance_unit to be 'm' or 'dm' or 'cm' or 'mm'."
            )
        if self.__clamp_distance is not None:
            self.__clamp_distance = length_unit_to_mm(
                self.__clamp_distance, clamp_distance_unit
            )
        self.__clamp_distance_unit = "mm"
        self.data_logger.log(self.__clamp_distance, "clamp_distance")
        self.data_logger.log(self.__clamp_distance_unit, "clamp_distance_unit")

    @property
    def cross_area(self) -> Optional[float]:
        """
        获取横截面积。

        :return: 横截面积。
        """
        return self.__cross_area

    @property
    def cross_area_unit(self) -> Optional[str]:
        """
        获取横截面积的单位。

        :return: 横截面积的单位。
        """
        return self.__cross_area_unit

    def set_cross_area(self, cross_area: float, cross_area_unit: str = "mm^2"):
        """
        设置横截面积。

        :param cross_area: 横截面积。
        :param cross_area_unit: 横截面积的单位。
        """
        if cross_area is not None and cross_area <= 0:
            raise ValueError("Expect cross_area to be greater than 0.")
        else:
            self.__cross_area = cross_area

        if cross_area_unit not in ["m^2", "dm^2", "cm^2", "mm^2"]:
            raise ValueError(
                "Expect cross_area_unit to be 'm^2' or 'dm^2' or 'cm^2' or 'mm^2'."
            )
        if self.__cross_area is not None:
            self.__cross_area = area_unit_to_mm2(self.__cross_area, cross_area_unit)
        self.__cross_area_unit = "mm^2"
        self.data_logger.log(self.__cross_area, "cross_area")
        self.data_logger.log(self.__cross_area_unit, "cross_area_unit")

    @property
    def speed(self) -> Optional[float]:
        """
        获取拉伸或压缩速度。

        :return: 拉伸或压缩速度。
        """
        return self.__speed

    @property
    def speed_unit(self) -> Optional[str]:
        """
        获取拉伸或压缩速度单位。

        :return: 拉伸或压缩速度单位。
        """
        return self.__speed_unit

    def set_speed(self, speed: float, speed_unit: str = "mm/s"):
        """
        设置拉伸或压缩速度及其单位。

        :param speed: 拉伸或压缩的速度。
        :param speed_unit:  拉伸或压缩速度的单位。
        """
        if speed is not None and speed <= 0:
            raise ValueError("Expect speed to be greater than 0.")
        else:
            self.__speed = speed

        if speed_unit not in [
            "m/h",
            "dm/h",
            "cm/h",
            "mm/h",
            "m/min",
            "dm/min",
            "cm/min",
            "mm/min",
            "m/s",
            "dm/s",
            "cm/s",
            "mm/s",
        ]:
            raise ValueError(
                "Expect speed_unit to be "
                "'m/h' or 'dm/h' or 'cm/h' or 'mm/h' or "
                "'m/min' or 'dm/min' or 'cm/min' or 'mm/min' or "
                "'m/s' or 'dm/s' or 'cm/s' or 'mm/s'."
            )

        if self.__speed is not None:
            self.__speed = speed_unit_to_mms(self.__speed, speed_unit)
        self.__speed_unit = "mm/s"
        self.data_logger.log(self.__speed, "speed")
        self.data_logger.log(self.__speed_unit, "speed_unit")

    @property
    def sampling_frequency(self) -> Optional[float]:
        """
        获取信号采集的频率。

        :return: 信号采集的频率。
        """
        return self.__sampling_frequency

    @property
    def sampling_frequency_unit(self) -> Optional[str]:
        """
        获取信号采集频率的单位。

        :return: 信号采集频率的单位。
        """
        return self.__sampling_frequency_unit

    def set_sampling_frequency(self, sampling_frequency: float,
                               sampling_frequency_unit: str = "Hz"):
        """
        设置信号采集的频率。
        :param sampling_frequency: 信号采集的频率值。
        :param sampling_frequency_unit: 信号采集频率的单位。
        """
        if sampling_frequency is not None and sampling_frequency <= 0:
            raise ValueError("Expect sampling_frequency to be greater than 0.")
        else:
            self.__sampling_frequency = sampling_frequency
        # 采样频率的单位只支持Hz，即：次/每秒。
        if sampling_frequency_unit not in ["Hz", "times/s"]:
            raise ValueError("Expect sampling_frequency_unit to be 'Hz' and 'times/s'.")
        self.__sampling_frequency_unit = "Hz"
        self.data_logger.log(self.__sampling_frequency, "sampling_frequency")
        self.data_logger.log(self.__sampling_frequency_unit, "sampling_frequency_unit")

    # 计算属性 -----------------------------------------------------------
    @property
    def sampling_interval(self) -> Optional[float]:
        """
        获取信号采集时间间隔。

        :return: 信号采集时间间隔。
        """
        if self.sampling_frequency is not None:
            return 1.0 / self.sampling_frequency
        return None

    @property
    def sampling_interval_unit(self) -> str:
        """
        获取信号采集时间间隔的单位。

        :return: 信号采集时间间隔的单位。
        """
        return "s"

    @property
    def theoretical_strain_rate(self) -> Optional[float]:
        """
        获取理论应变率。

        :return: 理论应变率。
        """
        if self.speed is not None and self.clamp_distance is not None:
            return self.speed / self.clamp_distance
        return None

    @property
    def theoretical_times(self) -> Optional[npt.NDArray[np.float64]]:
        """
        获取理论时间数据项。

        :return: 理论时间数据项。
        """
        if self.sampling_interval is not None:
            return self.data_nos.astype(np.float64) * self.sampling_interval
        return None

    # ----------------------------------------------------------------
    @property
    def copy_kwargs(self) -> dict:
        """
        拷贝此对象的可选关键字参数。

        :return: 拷贝得到的对象的可选关键字参数。
        """
        return copy.deepcopy(self.__kwargs)


# 定义结束 ==============================================================



