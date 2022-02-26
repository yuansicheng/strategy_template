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

class Dataset():
    def __init__(self) -> None:
        # {asset_name: Asset instance}
        # use ordereddict
        self.asset_dict = OrderedDict()

    def getAssetName(self, asset_file):
        return  os.path.basename(asset_file).split('.')[0]

    def addAsset(self, asset_file, transection_cost=0.001):
        assert os.path.exists(asset_file)

        asset_name = self.getAssetName(asset_file)
        if asset_name in list(self.asset_dict.keys()):
            logging.warning('Asset {} already loaded, now skip this file'.format(asset_name))

        self.asset_dict[asset_name] = Asset(asset_name, asset_file, transection_cost=transection_cost)

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
