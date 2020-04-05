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


def degree(r):
    """
    :param r: radian
    :return: degree
    """
    return r * 180.0 / math.pi


def lonlat_to_xyz(lon, lat):
    """
    :param lon: longitude
    :param lat: latitude
    :return: x, y, z in three dimension space
    """
    rad_lon = rad(lon)
    rad_lat = rad(lat)
    x = math.cos(rad_lat) * math.cos(rad_lon)
    y = math.cos(rad_lat) * math.sin(rad_lon)
    z = math.sin(rad_lat)
    return x, y, z


def xyz_to_lonlat(x, y, z):
    """
    :param x: x in three dimension space
    :param y: y in three dimension space
    :param z: z in three dimension space
    :return: longitude, latitude
    """
    rad_lat = math.asin(z)
    if y == 0.0 or math.cos(rad_lat) == 0.0:
        rad_lon = 0.0
    else:
        rad_lon = math.acos(z / math.cos(rad_lat))
        if math.asin(y / math.cos(rad_lat)) < 0.0:
            rad_lon = - rad_lon
    return rad_lon, rad_lat


def calc_cross_product(vector1, vector2):
    """
    :param vector1: (x1, y1, z1)
    :param vector2: (x2, y2, z2)
    :return: cross product vector
    """
    x1, y1, z1 = vector1
    x2, y2, z2 = vector2
    x = y1 * z2 - y2 * z1
    y = x2 * z1 - x1 * z2
    z = x1 * y2 - x2 * y1
    return x, y, z


def calc_dot_product(vector1, vector2):
    """
    :param vector1: (x1, y1, z1)
    :param vector2: (x2, y2, z2)
    :return: dot product vector
    """
    ret = 0.0
    for x1, x2 in zip(vector1, vector2):
        ret += x1 * x2
    return ret


def calc_euclid_distance(vector):
    """
    :param vector: (x, y, z)
    :return: euclid distance
    """
    ret = 0.0
    for x in vector:
        ret += x ** 2
    return math.sqrt(ret)


def is_same_direction(vector1, vector2):
    """
    :param vector1: (x1, y1, z1)
    :param vector2: (x2, y2, z2)
    :return: is two vector same direction
    """
    dot = calc_dot_product(vector1, vector2)
    length1 = calc_euclid_distance(vector1)
    length2 = calc_euclid_distance(vector2)
    if math.fabs(math.fabs(dot) - math.fabs(length1 * length2)) < df.ZERO_THRESHOLD:
        return True
    else:
        return False


def is_same_point(point1, point2):
    """
    :param point1: first point (longitude, latitude)
    :param point2: second point (longitude, latitude)
    :return:
    """
    return calc_point_distance(point1, point2) <= df.SAME_POINT_DISTANCE


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

    s_xyz = lonlat_to_xyz(s_point[df.INDEX_LON], s_point[df.INDEX_LAT])
    e_xyz = lonlat_to_xyz(e_point[df.INDEX_LON], e_point[df.INDEX_LAT])
    q_xyz = calc_cross_product(s_xyz, e_xyz)
    p_xyz = lonlat_to_xyz(point[df.INDEX_LON], point[df.INDEX_LAT])

    if is_same_direction(p_xyz, q_xyz):
        return s_point

    t_vector = calc_cross_product(p_xyz, q_xyz)
    k = 1.0 / calc_euclid_distance(t_vector)
    t_xyz = (k * t_vector[0], k * t_vector[1], k * t_vector[2])
    t_point = xyz_to_lonlat(t_xyz[0], t_xyz[1], t_xyz[2])
    if calc_point_distance(s_point, t_point) + calc_point_distance(e_point, t_point) > calc_point_distance(s_point, e_point):
        t_point = (-t_point[df.INDEX_LON], -t_point[df.INDEX_LAT])
    return t_point


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
