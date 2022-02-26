#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging

import pandas as pd
import numpy as np

class Asset():
    def __init__(self, asset_name, asset_file, transection_cost=0.001) -> None:
        self.asset_name = asset_name
        self.asset_file = asset_file
        self.transection_cost = transection_cost

    def loadAllData(self):
        if self.asset_file.endswith('.csv'):
            df = pd.read_csv(self.asset_file)
        elif self.asset_file.endswith('.xls') or self.asset_file.endswith('.xlsx'):
            df = pd.read_excel(self.asset_file)
        df.index = pd.to_datetime(df['date'])
        df.drop(columns=['date'])
        return df

    def getData(self, date_list):
        all_data = self.loadAllData()
        assert date_list[-1] < all_data.index[-1]
        df = pd.DataFrame(index=date_list, columns=all_data.columns)
        df.iloc[:,:] = np.nan
        exist_date_list = [d for d in all_data.index if d in date_list]
        df.loc[exist_date_list] = all_data.loc[exist_date_list]
        # if miss the first value, then break
        assert not np.isnan(df['CLOSE'].iloc[0])
        missing_date = set(df[df['CLOSE'].isnull().values==True].index)
        df.fillna(method='ffill', inplace=True)

        return df, missing_date

