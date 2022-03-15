#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging

import pandas as pd
import numpy as np

class Asset():
    def __init__(self, asset_name, asset_file, transection_cost=0., weight_range=[0., 1.]) -> None:
        self.asset_name = asset_name
        self.asset_file = asset_file
        self.transection_cost = transection_cost

        assert len(weight_range) == 2, 'len(weight_range) must be 2'
        self.weight_range = weight_range

    def loadAllData(self):
        if self.asset_file.endswith('.csv'):
            df = pd.read_csv(self.asset_file, encoding='utf-8-sig')
        elif self.asset_file.endswith('.xls') or self.asset_file.endswith('.xlsx'):
            df = pd.read_excel(self.asset_file)
        date_label = self.findLabel(df.columns, ['date', '日期'])
        df.index = pd.to_datetime(df[date_label])
        df.drop(columns=[date_label])
        return df

    def findLabel(self, columns, labels):
        # find which column contains target label
        labels = [label.lower() for label in labels]
        for column in columns:
            if column.lower() in labels:
                return column
        logging.error('Can not find a colomn in asset {} with label {}'.format(self.asset_name, labels))
        sys.exit(1)

    def getData(self, date_list):
        all_data = self.loadAllData()
        assert date_list[-1] < all_data.index[-1], 'date_list[-1] < all_data.index[-1]'
        df = pd.DataFrame(index=date_list, columns=all_data.columns)
        df.iloc[:,:] = np.nan
        exist_date_list = [d for d in all_data.index if d in date_list]
        df.loc[exist_date_list] = all_data.loc[exist_date_list]
        # if miss the first value, then break
        close_label = self.findLabel(df.columns, ['CLOSE', '收盘价'])
        df['CLOSE'] = df[close_label]
        assert not np.isnan(df['CLOSE'].iloc[0]), 'First close data must not be empty'
        missing_date = set(df[df['CLOSE'].isnull().values==True].index)
        df.fillna(method='ffill', inplace=True)

        return df, missing_date

