# -*- coding: utf-8 -*- 
# @Time : 2019/11/10 4:36 PM 
# @Author : yangyuxin
# @File : file_operator.py


import os
import sys
import ogr


def create_feature(field_dict, geometry):
    field_names = field_dict.keys()
    feat_defn = create_featuredefn(field_names)
    feature = ogr.Feature(feat_defn)
    for key, value in field_dict.items():
        feature.SetField(key, value)
    feature.SetGeometry(geometry)
    return feature


def create_featuredefn(field_names):
    feat_defn = ogr.FeatureDefn()
    fieldDef_list = create_fieldDef_list(field_names)
    for fieldDef in fieldDef_list:
        feat_defn.AddFieldDefn(fieldDef)
    return feat_defn


def create_fieldDef_list(field_names):
    fieldDef_list = list()
    for index in range(len(field_names)):
        fieldDef = ogr.FieldDefn()
        fieldDef.SetType(ogr.OFTString)
        fieldDef.SetName(field_names[index])
        fieldDef.SetWidth(20)
        fieldDef_list.append(fieldDef)
    return fieldDef_list


def create_miffile(file_path, fieldDef_list) :
    ds_file = None
    ds_driver = None
    lyr_file = None
    lyr_name = ""
    pos = file_path.rfind('.')
    if pos != -1 :
        lyr_name = file_path[0 : pos]
    pos = lyr_name.rfind(os.sep)
    if pos != -1 :
        lyr_name = lyr_name[pos + 1 : len(lyr_name)]
    ds_driver = ogr.GetDriverByName("MapInfo File")
    if ds_driver is None :
        return ds_file
    ds_file = ds_driver.CreateDataSource(file_path)
    if ds_file is None :
        return ds_file
    lyr_file = ds_file.CreateLayer(lyr_name)
    if lyr_file is None :
        ds_file = None
        return ds_file
    for fieldDef in fieldDef_list:
        lyr_file.CreateField(fieldDef)
    return ds_file


class FileReader(object):
    def __init__(self, file_path):
        self.ds_file = ogr.Open(file_path)
        if self.ds_file:
            self.lyr_file = self.ds_file.GetLayerByIndex(0)

    def is_valid(self):
        return self.ds_file and self.lyr_file

    def get_lyr_file(self):
        if not self.is_valid():
            return None

        self.lyr_file.ResetReading()
        return self.lyr_file

    def get_field_def_list(self):
        if not self.is_valid():
            return None

        field_def_list = []
        feature = self.lyr_file.GetNextFeature()
        for i in range(feature.GetFieldCount()):
            field_def_list.append(feature.GetFieldDefnRef(i))
        return field_def_list


class FileWriter(object):
    def __init__(self, file_path, field_def_list):
        self.ds_file = create_miffile(file_path, field_def_list)
        if self.ds_file:
            self.lyr_file = self.ds_file.GetLayerByIndex(0)

    def is_valid(self):
        return self.ds_file and self.lyr_file

    def write_feature(self, feature):
        if not self.is_valid():
            return False
        self.lyr_file.CreateFeature(feature)
        return True



