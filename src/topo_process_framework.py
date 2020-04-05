# -*- coding: utf-8 -*- 
# @Time : 2020/2/2 8:55 PM 
# @Author : yangyuxin
# @File : topo_process_framework.py
# 这个代码是对数据进行有关拓扑的处理的框架


import os
import sys
import ogr

import pyqtree
import data_define as df
import distance_process
import file_operator


class Node(object):
    def __init__(self, feature=None, link_list=None):
        """
        :param feature: node feature, ogr.Feature
        :param link_list: connect links of node, [Link]
        """
        self.feature = feature
        self.link_list = link_list if link_list else list()

    def __del__(self):
        self.feature = None
        self.link_list = None


class Link(object):
    def __init__(self, feature=None, snode=None, enode=None):
        """
        :param feature: link feature, ogr.Feature
        :param snode: start node of feature, Node
        :param enode: end node of feature, Node
        """
        self.feature = feature
        self.snode = snode
        self.enode = enode

    def __del__(self):
        self.feature = None
        self.snode = None
        self.enode = None


class TopoFramework(object):
    """
    use road features to build topology relationship
    """
    def __init__(self, road_layer):
        self.road_features = [feature for feature in road_layer]
        self.link_list = list()
        self.node_list = list()
        self.spatial_index = None

    def __del__(self):
        for feature in self.road_features:
            feature.Destory()

    def init_topology(self):
        # init spatial index
        qt_box = None
        for feature in self.road_features:
            box = get_feature_box(feature)
            qt_box = max(qt_box, box) if qt_box else box
        self.spatial_index = pyqtree.Index(qt_box)

        # add link feature in index
        for feature in self.road_features:
            box = get_feature_box(feature)
            link = Link(feature)
            self.spatial_index.insert(link, box)
            self.link_list.append(link)

        # build topology relationship
        for link in self.link_list:
            geometry = link.feature.GetGeometryRef()
            points = geometry.GetPoints()
            s_point = points[0]
            e_point = points[-1]
            if not link.snode:
                self._create_node(s_point)
            if not link.enode:
                self._create_node(e_point)

    def _create_node(self, point):
        if self.spatial_index is None:
            return

        feature = file_operator.create_feature({}, point_to_geometry(point))
        node = Node(feature)

        box = get_point_box(point, df.ZERO_THRESHOLD)
        near_links = self.spatial_index.intersect(box)
        for near_link in near_links:
            near_geometry = near_link.feature.GetGeometryRef()
            near_points = near_geometry.GetPoints()
            near_s_point = near_points[0]
            near_e_point = near_points[-1]
            if is_same_point(near_s_point, point):
                node.link_list.append(near_link)
                near_link.snode = node
            if is_same_point(near_e_point, point):
                node.link_list.append(near_link)
                near_link.enode = node
        self.node_list.append(node)

    def get_links(self):
        return self.link_list

    def get_nodes(self):
        return self.node_list


class TopoFrameWork2(object):
    """
    use road features and node features to build relationship
    """
    def __init__(self, road_layer, node_layer):
        self.road_features = [feature for feature in road_layer]
        self.node_features = [feature for feature in node_layer]
        self.key_node_dict = dict()
        self.link_list = list()
        self.node_list = list()

    def __del__(self):
        for feature in self.road_features:
            feature.Destory()
        for feature in self.node_features:
            feature.Destory()

    def init_topology(self):
        # init node key relationship
        for feature in self.node_features:
            node = Node(feature)
            key = self._get_node_key(feature)
            self.key_node_dict[key] = node
            self.node_list.append(node)

        # build topology relationship
        for feature in self.road_features:
            snode_key = self._get_snode_key(feature)
            enode_key = self._get_enode_key(feature)
            snode = self.key_node_dict.get(snode_key, None)
            enode = self.key_node_dict.get(enode_key, None)
            link = Link(feature, snode, enode)
            if snode:
                snode.link_list.append(link)
            if enode:
                enode.link_list.append(link)

    def _get_node_key(self, feature):
        # use geometry as key. you can identify your own key.
        geometry = feature.GetGeometryRef()
        pt = geometry.GetPoint()
        key = "|".join([str(pt[df.INDEX_LON]), str(pt[df.INDEX_LAT])])
        return key

    def _get_snode_key(self, feature):
        # use geometry as key. you can identify your own key.
        geometry = feature.GetGeometryRef()
        pt = geometry.GetPoint(0)
        key = "|".join([str(pt[df.INDEX_LON]), str(pt[df.INDEX_LAT])])
        return key

    def _get_enode_key(self, feature):
        # use geometry as key. you can identify your own key.
        geometry = feature.GetGeometryRef()
        pt = geometry.GetPoint(geometry.GetPointCount() - 1)
        key = "|".join([str(pt[df.INDEX_LON]), str(pt[df.INDEX_LAT])])
        return key


def get_feature_box(feature, buffer=0.0):
    return get_geometry_box(feature.GetGeometryRef(), buffer)


def get_geometry_box(geometry, buffer=0.0):
    # return [x_min, y_min, x_max, y_max]
    box = [0, 0, 0, 0]
    if geometry is None or geometry.IsEmpty():
        return box
    env = list(geometry.GetEnvelope())
    box = [env[0] - buffer, env[2] - buffer, env[1] + buffer, env[3] + buffer]
    return box


def get_point_box(point, buffer=0.0):
    x = point[0]
    y = point[1]
    return [x - buffer, y - buffer, x + buffer, y + buffer]


def max_box(box1, box2):
    # box [x_min, y_min, x_max, y_max]
    x_min = min(box1[0], box2[0])
    y_min = min(box1[1], box2[1])
    x_max = max(box1[2], box2[2])
    y_max = max(box1[3], box2[3])
    return [x_min, y_min, x_max, y_max]


def is_same_point(point1, point2):
    # you can realize your version function
    lon_same = point1[df.INDEX_LON] == point2[df.INDEX_LON]
    lat_same = point1[df.INDEX_LAT] == point2[df.INDEX_LAT]
    return lon_same and lat_same


def point_to_geometry(point):
    geometry = ogr.Geometry(ogr.wkbPoint)
    geometry.AddPoint(point[df.INDEX_LON], point[df.INDEX_LAT])
    return geometry
