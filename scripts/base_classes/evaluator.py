#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-01-01 

import os, sys, argparse, logging

from datetime import datetime, timedelta, date

import pandas as pd
import numpy as np

def strfTime(t):
    return t.strftime("%Y%m%d")

class Evaluator:
    def __init__(self, asset_df=None, args=None) -> None:
        self.df = asset_df
        self.daily_yield = (self.df / self.df.shift() - 1).dropna()
        self.args = args

        self.evaluation = pd.DataFrame(
            columns=self.df.columns,
        )

    def calculateReturnDevideYear(self) -> None:
        # extract years
        years = set([i.year for i in self.df.index])
        last_year_value_flag = False
        for year in sorted(list(years)):
            tmp = self.df.loc[str(year)]
            if not last_year_value_flag:
                last_year_value = tmp.iloc[0]
                last_year_value_flag = True
            # logging.debug((year, tmp.iloc[-1], last_year_value))
            self.evaluation.loc[year] = 100 * ((tmp.iloc[-1] / last_year_value) ** (self.args.DAY_OF_YEAR/tmp.shape[0]) - 1)
            last_year_value = tmp.iloc[-1]

    def calculateTotalReturn(self) -> None:
        self.evaluation.loc['累计收益率'] = 100 * (self.df.iloc[-1] / self.df.iloc[0] -1)

    def calculateAnnualizedReturn(self) -> None:
        self.evaluation.loc['年化收益率'] = 100 * ((self.df.iloc[-1] / self.df.iloc[0]) ** (self.args.DAY_OF_YEAR/self.df.shape[0]) - 1)

    def calculateAnnualizedVolatility(self) -> None:
        self.evaluation.loc['年化波动率'] = 100 * self.daily_yield.std() * (self.args.DAY_OF_YEAR**0.5) 
        # print( self.evaluation.loc['年化波动率'])

    def calculateSharpeRatio(self) -> None:
        assert '年化收益率' in self.evaluation.index
        assert '年化波动率' in self.evaluation.index
        self.evaluation.loc['sharp比率'] = (self.evaluation.loc['年化收益率'] - self.args.RFR*100) / self.evaluation.loc['年化波动率']

    def calculateCalmarRatio(self) -> None:
        assert '年化收益率' in self.evaluation.index
        assert '最大回撤' in self.evaluation.index
        self.evaluation.loc['calmar比率'] = (self.evaluation.loc['年化收益率'] - self.args.RFR*100) / self.evaluation.loc['最大回撤']

    def calculateMaxLoss(self) -> None:
        self.evaluation.loc['最大回撤'] = np.nan
        self.evaluation.loc['最大回撤发生区间'] = np.nan
        def getAssetMaxLoss(data):
            data = np.array(data)
            max_loss = 0
            # loop
            for i in range(1, len(data)):
                this_max_loss = (data[:i].max() - data[i:].min()) / data[:i].max()
                if this_max_loss > max_loss:
                    max_loss = this_max_loss
                    max_loss_range = (data[:i].argmax(), i+data[i:].argmin())
            return max_loss * 100, max_loss_range


        for asset in self.df.columns:
            max_loss, max_loss_range = getAssetMaxLoss(self.df[asset])
            self.evaluation.loc['最大回撤', asset] = max_loss
            self.evaluation.loc['最大回撤发生区间', asset] = '{}-{}'.format(strfTime(self.df.index[max_loss_range[0]]), strfTime(self.df.index[max_loss_range[1]]))

    def calculateLongestLoss(self) -> None:
        def getLongestLoss(data):
            index = list(data.index)
            data = list(data) + [1e6]
            longest_loss = 0
            i_loss_start = 0
            for i in range(1, len(data)):
                if data[i] >= data[i_loss_start]:
                    this_loss = (index[i-1]-index[i_loss_start]).days
                    if this_loss > longest_loss:
                        longest_loss = this_loss 
                        longest_loss_range = (i_loss_start, i-1)
                    i_loss_start = i
            return longest_loss, longest_loss_range
                    
        for asset in self.df.columns:
            longest_loss, longest_loss_range = getLongestLoss(self.df[asset])
            self.evaluation.loc['最长回撤持续时间', asset] = longest_loss
            self.evaluation.loc['最长回撤发生区间', asset] = '{}-{}'.format(strfTime(self.df.index[longest_loss_range[0]]), strfTime(self.df.index[longest_loss_range[1]]))

    def calculateSortinoRatio(self) -> None:
        mar = self.args.RFR
        def getSortinoDenominator(data):
            nonlocal mar
            daily_mar = (1+mar) ** (1/self.args.DAY_OF_YEAR) - 1
            data[data>daily_mar] = np.nan
            return (((data.dropna() - daily_mar)**2).sum() / (data.dropna().shape[0]-1)) ** 0.5
        self.evaluation.loc['sortino比率'] = (self.evaluation.loc['年化收益率']/100-mar) / self.daily_yield.apply(getSortinoDenominator)

    def calculateInformationRatio(self) -> None:
        numerator = 0.01 * self.evaluation.loc['年化收益率'].apply(lambda x: self.evaluation.loc['年化收益率'].iloc[0] - x)
        denominator = self.daily_yield.apply(lambda x: self.daily_yield.iloc[:, 0] - x).std()
        self.evaluation.loc['信息比率(策略相对于资产)'] = numerator / denominator
        self.evaluation.loc['信息比率(策略相对于资产)'].iloc[0] = '--'
        

    def evaluate(self) -> pd.DataFrame:
        self.calculateReturnDevideYear()
        self.calculateTotalReturn()
        self.calculateAnnualizedReturn()
        self.calculateAnnualizedVolatility()
        self.calculateMaxLoss()
        self.calculateLongestLoss()
        self.calculateSharpeRatio()
        self.calculateCalmarRatio()
        self.calculateSortinoRatio()
        self.calculateInformationRatio()

        return self.evaluation



