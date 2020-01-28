# -*- coding: utf-8 -*- 
# @Time : 2019/11/17 4:49 PM 
# @Author : yangyuxin
# @File : distance_process.py
# 这个代码文件用来处理球面空间条件下距离计算的相关问题，传入的参数均为经纬度
# 返回的距离均为米


import math
import copy
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
    if is_same_point(s_point, e_point):
        return copy.deepcopy(s_point)
    if is_same_point(point, s_point):
        return copy.deepcopy(s_point)
    if is_same_point(point, e_point):
        return copy.deepcopy(e_point)

    # otherwise use comp.graphics.algorithms Frequently Asked Questions method */
    # (1)                AC dot AB
    #               r = ---------
    #                   ||AB||^2
    #    r has the following meaning:
    #    r=0 P = A
    #    r=1 P = B
    #    r<0 P is on the backward extension of AB
    #    r>1 P is on the forward extension of AB
    #    0<r<1 P is interior to AB
    #
    # A: point
    # B: s_point
    # C: e_point
    s_vector_x = point[df.INDEX_LON] - s_point[df.INDEX_LON]
    s_vector_y = point[df.INDEX_LAT] - s_point[df.INDEX_LAT]
    line_vector_x = e_point[df.INDEX_LON] - s_point[df.INDEX_LON]
    line_vector_y = e_point[df.INDEX_LAT] - s_point[df.INDEX_LAT]
    r = (s_vector_x * line_vector_x + s_vector_y * line_vector_y) / (line_vector_x ** 2 + line_vector_y ** 2)

    if r < 0.0:
        return copy.deepcopy(s_point)
    if r > 1.0:
        return copy.deepcopy(e_point)

    foot_point_x = s_point[df.INDEX_LON] + r * line_vector_x
    foot_point_y = s_point[df.INDEX_LAT] + r * line_vector_y
    return foot_point_x, foot_point_y


def calc_point_to_line_distance(point, line):
    """
    :param point: point (longitude, latitude)
    :param line: line [points]
    :return: distance of point and line. the unit is metre
    """
    nearest_point = calc_nearest_point_on_line(point, line)
    if nearest_point:
        return calc_point_distance(point, nearest_point)
    else:
        return None


def calc_line_length(line):
    """
    :param line: line [points]
    :return: length of line. the unit is metre
    """
    length = 0
    for i in range(len(line) - 1):
        length += calc_point_distance(line[i], line[i+1])
    return length


def split_line_by_length(line, length):
    """
    :param line: line [points]
    :param length: length of one part
    :return: lines [line]
    """
    if len(line) <= 1 or length <= 0.0:
        return list()

    part_length = 0.0
    part_line = list()
    ret_lines = list()
    for i in range(len(line) - 1):
        pt1 = line[i]
        pt2 = line[i + 1]
        part_length += calc_point_distance(pt1, pt2)
        part_line.append(pt1)
        if part_length == length:
            ret_lines.append(part_line)
            part_line = [pt1]
        elif part_length > length:
            mid_pt = calc_mid_point_by_length(pt2, pt1, length - part_length)
            part_line.append(mid_pt)
            ret_lines.append(part_line)
            part_line = [mid_pt]
        else:
            pass
    part_line.append(line[-1])
    ret_lines.append(part_line)
    return ret_lines


def get_start_part_by_length(line, length):
    """
    :param line: line [points]
    :param length: length of start part
    :return: start part line
    """
    if len(line) <= 1 or length <= 0.0:
        return list()

    part_length = 0.0
    part_line = list()
    for i in range(len(line) - 1):
        pt1 = line[i]
        pt2 = line[i + 1]
        part_length += calc_point_distance(pt1, pt2)
        part_line.append(pt1)
        if part_length == length:
            break
        elif part_length > length:
            mid_pt = calc_mid_point_by_length(pt2, pt1, length - part_length)
            part_line.append(mid_pt)
            break
        else:
            pass
    return part_line


def get_end_part_by_length(line, length):
    """
    :param line: line [points]
    :param length: length of end part
    :return: end part line
    """
    if len(line) <= 1 or length <= 0.0:
        return list()

    part_length = 0.0
    part_line = list()
    for i in range(len(line), 1):
        pt1 = line[i]
        pt2 = line[i - 1]
        part_length += calc_point_distance(pt1, pt2)
        part_line.append(pt1)
        if part_length == length:
            break
        elif part_length > length:
            mid_pt = calc_mid_point_by_length(pt2, pt1, length - part_length)
            part_line.append(mid_pt)
            break
        else:
            pass
    return part_line


def get_start_part_by_percent(line, percent):
    """
    :param line: line [points]
    :param percent: percent of start part
    :return: start part line
    """
    if percent <= 0.0:
        return list()
    if percent >= 1.0:
        return line

    line_length = calc_line_length(line)
    part_length = line_length * percent
    return get_start_part_by_length(line, part_length)


def get_end_part_by_percent(line, percent):
    """
    :param line: line [points]
    :param percent: percent of end part
    :return: end part line
    """
    if percent <= 0.0:
        return list()
    if percent >= 1.0:
        return line

    line_length = calc_line_length(line)
    part_length = line_length * percent
    return get_end_part_by_length(line, part_length)


def calc_mid_point_by_length(s_point, e_point, length):
    """
    :param s_point: start point (longitude, latitude)
    :param e_point: end point (longitude, latitude)
    :param length: length from start point
    :return: mid point on line
    """
    line_length = calc_point_distance(s_point, e_point)
    percent = length / line_length
    return calc_mid_point_by_percent(s_point, e_point, percent)


def calc_mid_point_by_percent(s_point, e_point, percent):
    """
    :param s_point: start point (longitude, latitude)
    :param e_point: end point (longitude, latitude)
    :param percent: percent from start point
    :return: mid point on line
    """
    if percent <= 0.0:
        return s_point
    if percent >= 1.0:
        return e_point

    s_lon = s_point[df.INDEX_LON]
    s_lat = s_point[df.INDEX_LAT]
    e_lon = e_point[df.INDEX_LON]
    e_lat = e_point[df.INDEX_LAT]
    d_lon = e_lon - s_lon
    d_lat = e_lat - s_lat
    m_lon = s_lon + percent * d_lon
    m_lat = s_lat + percent * d_lat
    return m_lon, m_lat
