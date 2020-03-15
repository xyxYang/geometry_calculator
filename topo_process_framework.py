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
    def __init__(self, road_layer):
        self.road_features = [feature for feature in road_layer]
        self.link_list = list()
        self.node_list = list()

    def __del__(self):
        for feature in self.road_features:
            feature.Destory()

    def init_topology(self):
        # init spatial index
        qt_box = None
        for feature in self.road_features:
            box = get_feature_box(feature)
            qt_box = max(qt_box, box) if qt_box else box
        spatial_index = pyqtree.Index(qt_box)

        # add link feature in index
        for feature in self.road_features:
            box = get_feature_box(feature)
            link = Link(feature)
            spatial_index.insert(link, box)
            self.link_list.append(link)

        # build topology relationship
        for link in self.link_list:
            pass


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


def max_box(box1, box2):
    # box [x_min, y_min, x_max, y_max]
    x_min = min(box1[0], box2[0])
    y_min = min(box1[1], box2[1])
    x_max = max(box1[2], box2[2])
    y_max = max(box1[3], box2[3])
    return [x_min, y_min, x_max, y_max]
