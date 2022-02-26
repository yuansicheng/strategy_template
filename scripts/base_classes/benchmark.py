#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging

from collections import OrderedDict
import pandas as pd
import numpy as np

from base_classes.dataset import Dataset

class Benchmark(Dataset):
    def __init__(self, benchmark_name='benchmark') -> None:
        super().__init__()

        self.benchmark_name = benchmark_name
        self.asset_dict = OrderedDict()
        self.asset_weight = OrderedDict()

    def addAsset(self, asset_file, weight):
        super().addAsset(asset_file)
        self.asset_weight[self.getAssetName(asset_file)] = weight

    def getValue(self, date_list):
        weights = np.array(list(self.asset_weight.values()))
        assert weights.sum() == 1
        raw_data, _ = self.getData(date_list)

        transection_cost = self.getTransectionCost()

        close_data = self.dict2CloseDf(raw_data)
        return pd.DataFrame({self.benchmark_name: (close_data * weights).sum(axis=1) - (weights * close_data.iloc[0] * transection_cost).sum()})
        
        



# # test
# bm = Benchmark()
# bm.addAsset('data/沪深300指数(全收益).csv', 0.3)
# bm.addAsset('data/中债-国债总财富(总值)指数.csv', 0.7)
# print(bm.asset_dict)