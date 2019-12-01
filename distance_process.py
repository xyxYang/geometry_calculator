# -*- coding: utf-8 -*- 
# @Time : 2019/11/17 4:49 PM 
# @Author : yangyuxin
# @File : distance_process.py
# 这个代码文件用来处理球面空间条件下距离计算的相关问题，传入的参数均为经纬度
# 返回的距离均为米


import math
import data_define as df


EARTH_RADIUS = 6378137  # metre


def rad(d):
    """
    :param d: degree
    :return: radian
    """
    return d * math.pi / 180.0


def is_same_point(point1, point2):
    """
    :param point1: first point (longitude, latitude)
    :param point2: second point (longitude, latitude)
    :return:
    """
    return calc_point_distance(point1, point2) < df.SAME_POINT_DISTANCE


def calc_point_distance(point1, point2):
    """
    :param point1: first point
    :param point2: second point
    :return: distance of two point. the unit is metre
    """
    radLat1 = rad(point1[df.INDEX_LAT])
    radlng1 = rad(point1[df.INDEX_LON])
    radLat2 = rad(point2[df.INDEX_LAT])
    radlng2 = rad(point2[df.INDEX_LON])
    a = radLat1 - radLat2
    b = radlng1 - radlng2
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b / 2), 2)))
    s = s * EARTH_RADIUS
    s = (s * 10000 + 0.5) / 10000
    return s


def calc_nearest_point_on_line(point, line):
    """
    :param point: point (longitude, latitude)
    :param line: line [points]
    :return: point on line (longitude, latitude)
    """
    point_num = len(line)
    if point_num == 0:
        return None
    if point_num == 1:
        return line[0]

    min_distance = float('inf')
    min_point = None
    for i in range(point_num - 1):
        s_point = line[i]
        e_point = line[i + 1]
        near_point = calc_nearest_point_on_line_segment(point, s_point, e_point)
        distance = calc_point_distance(point, near_point)
        if distance < min_distance:
            min_distance = distance
            min_point = near_point

    if min_point is None:
        print("calc nearest point error")
    return min_point


def calc_nearest_point_on_line_segment(point, s_point, e_point):
    """
    :param point: point (longitude, latitude)
    :param s_point: start point of line segment (longitude, latitude)
    :param e_point: end point of line segment (longitude, latitude)
    :return: point on line segment (longitude, latitude)
    """
    # TODO


