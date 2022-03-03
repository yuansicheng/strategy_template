#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging
from datetime import datetime

import pandas as pd

class DateManager():
    def __init__(self, date_file) -> None:
        self.date_file = date_file
        self.setAllDateList()

    def setAllDateList(self):
        self.all_date = pd.read_csv(self.date_file, encoding = 'gb2312')
        self.all_date.index = [pd.to_datetime(d) for d in self.all_date['日期序列']]

    def getDateList(self, date_range, buffer=0):
        assert len(date_range) == 2
        assert self.all_date.index[0] < date_range[0] < date_range[1] < self.all_date.index[-1]
        assert buffer >=0
        before_shape =  self.all_date.loc[:date_range[0]].shape[0]
        assert before_shape >= buffer
        return self.all_date.loc[:date_range[1]].iloc[before_shape-buffer:].index

    def getUpdateDateList(self, date_range, frequency=1, missing_date=None):
        assert isinstance(frequency, int) or frequency in ['weekly', 'monthly', 'quarterly']
        date_list = self.getDateList(date_range)
        if missing_date:
            date_list = [d for d in date_list if d not in missing_date]
        if isinstance(frequency, int):
            return [date_list[i] for i in range(len(date_list)) if i % frequency==0]
        tmp = pd.DataFrame()
        tmp['date'] = date_list
        tmp['year'] = [d.year for d in date_list]
        if frequency == 'weekly':
            tmp['week_of_year'] = [d.weekofyear for d in date_list]
            return tmp.groupby(['year', 'week_of_year']).first()['date']
        if frequency == 'monthly':
            tmp['month'] = [d.month for d in date_list]
            return tmp.groupby(['year', 'month']).first()['date']
        if frequency == 'quarterly':
            tmp['quarter'] = [(d.month+1)//3 for d in date_list]
            return tmp.groupby(['year', 'quarter']).first()['date']

    

# # test
# dm = DateManager('scripts/base_classes/transection_date.csv')
# date_range = [datetime(2010,1,1), datetime(2011,1,1)]
# print(dm.getUpdateDateList(date_range, frequency='weekly'))

    
    