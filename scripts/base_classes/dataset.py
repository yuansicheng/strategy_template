#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging
from collections import OrderedDict
import pandas as pd
import numpy as np

from base_classes.asset import Asset

class Group():
    def __init__(self, name='', transection_cost=0., weight_range=[0., 1.]) -> None:
        self.name = name
        self.transection_cost = transection_cost
        self.children = OrderedDict()
        self.assets = OrderedDict()

        assert len(weight_range) == 2, 'len(weight_range) must be 2'
        self.weight_range = weight_range
        
    def getAllLeafAsset(self):
        all_leaf = list(self.assets.keys())
        for g in self.children.values():
            all_leaf += g.getAllLeafAsset()
        return all_leaf

class Dataset():
    def __init__(self) -> None:
        # {asset_name: Asset instance}
        # use ordereddict
        self.asset_dict = OrderedDict()

        # init root group
        self.group = Group(name='root')

    def getAssetName(self, asset_file):
        return os.path.basename(asset_file).split('.')[0]

    def addGroup(self, group='', weight_range=[0., 1.]):
        group_split = group.split('/')
        group_split = [s for s in group_split if s]
        if not group_split:
            return
        tmp = self.group
        for name in group_split:
            if name not in tmp.children:
                tmp.children[name] = Group(name=name, weight_range=weight_range)
            tmp = tmp.children[name]

    def getGroup(self, group=''):
        group_split = group.split('/')
        group_split = [s for s in group_split if s]
        if not group_split:
            return self.group
        tmp = self.group
        for name in group_split:
            assert name in tmp.children, 'group {} have not registered'.format(group)
            tmp = tmp.children[name]
        return tmp

    def printGroup(self, g, level=0):
        if level == 0:
            print('#'*50)
            print('All groups and assets you are currently registered')
            print('#'*50)
        print('\t'*level, 'group:', g.name, g.weight_range)
        for asset in g.assets:
            print('\t'*(level+1), 'asset:', asset, g.assets[asset].weight_range)
        for g in g.children.values():
            self.printGroup(g, level=level+1)
        if level == 0:
            print('#'*50)



    def addAsset(self, asset_file, transection_cost=0., group='', weight_range=[0., 1.]):
        assert os.path.exists(asset_file), 'asset_file {} do not exists'.format(asset_file)

        asset_name = self.getAssetName(asset_file)
        if asset_name in list(self.asset_dict.keys()):
            logging.warning('Asset {} already loaded, now skip this file'.format(asset_name))
            return

        this_group = self.getGroup(group=group)
        if not transection_cost:
            transection_cost = this_group.transection_cost

        self.asset_dict[asset_name] = Asset(asset_name, asset_file, transection_cost=transection_cost, weight_range=weight_range)

        this_group.assets[asset_name] = self.asset_dict[asset_name]

        

    def getTransectionCost(self):
        return np.array([v.transection_cost for v in self.asset_dict.values()])

    def getData(self, date_list):
        raw_data = self.asset_dict.copy()
        missing_date = set()
        for asset_name, asset in self.asset_dict.items():
            # raw_data and missing_date -> rd and md
            rd, md = asset.getData(date_list)
            raw_data[asset_name] = rd
            missing_date.update(md)
        return raw_data, missing_date

    def dict2CloseDf(self, data_dict):
        close_df = pd.DataFrame({k:v['CLOSE'] for k,v in data_dict.items()})
        return close_df / close_df.iloc[0]


# # test
# from glob import glob
# dataset = Dataset()
# asset_files = glob('data/*债*')
# for asset in asset_files:
#     dataset.addAsset(asset)
# print(dataset.asset_dict['中债-信用债总财富(总值)指数'].asset_file)
# print(dataset.asset_dict['中债-信用债总财富(总值)指数'].loadAllData())
