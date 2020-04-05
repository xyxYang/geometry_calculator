# -*- coding: utf-8 -*- 
# @Time : 2020/1/28 7:22 PM 
# @Author : yangyuxin
# @File : angle_process.py
# 这个代码文件用来处理经纬度角度计算的相关问题，输入参数为经纬度
# 返回结果为度


import math
import copy
import data_define as df


def eqaul(a, b):
    return math.fabs(a - b) < 0.000000001


def degree(r):
    """
    :param r: radian
    :return: degree
    """
    return r * 180 / math.pi


def calc_line_angle(line):
    """
    :param line: line [points]
    :return: angle from north, clockwise. the unit is degree.
    """
    if len(line) <= 1:
        return None

    s_pt = line[0]
    e_pt = line[-1]
    delta_lon = e_pt[df.INDEX_LON] - s_pt[df.INDEX_LON]
    delta_lat = e_pt[df.INDEX_LAT] - s_pt[df.INDEX_LAT]

    if eqaul(delta_lon, 0.0) and eqaul(delta_lat, 0.0):
        return 0.0

    if eqaul(delta_lat, 0.0):
        if delta_lon > 0.0:
            return 90.0
        else:
            return 270.0

    if eqaul(delta_lon, 0.0):
        if delta_lat > 0.0:
            return 0.0
        else:
            return 180.0

    if delta_lat > 0.0:
        if delta_lon > 0.0:
            return degree(math.atan(delta_lon / delta_lat))
        else:
            return 360.0 - degree(math.atan(delta_lon / delta_lat))
    else:
        if delta_lon > 0.0:
            return 180.0 - degree(math.atan(delta_lon / delta_lat))
        else:
            return 180.0 + degree(math.atan(delta_lon / delta_lat))

    return 0.0



def calc_line2line_angle(line1, line2):
    """
    :param line1: line1 [points]
    :param line2: line2 [points]
    :return: angle between two lines, clockwise. the unit is degree.
    """
    angle1 = calc_line_angle(line1)
    angle2 = calc_line_angle(line2)
    if not (angle1 and angle2):
        return None

    angle = angle2 - angle1
    if angle < 0.0:
        angle += 360.0
    return angle
