# -*- coding: utf-8 -*- 
# @Time : 2020/2/2 8:55 PM 
# @Author : yangyuxin
# @File : topo_process_framework.py
# 这个代码是对数据进行有关拓扑的处理的框架


import os
import sys
import ogr

import pyqtree


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
    def __init__(self):
        pass

    def __del__(self):
        pass
