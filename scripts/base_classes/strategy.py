#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging

from abc import ABC, abstractmethod

import pandas as pd
from tqdm import tqdm
import numpy as np


class Strategy(ABC):
    def __init__(self,
                 dataset = None, 
                 date_manager = None, 
                 args = None, 
                 **kwargs, 
                 ) -> None:
        super().__init__()

        assert dataset
        self.dataset = dataset

        assert date_manager
        self.date_manager = date_manager

        assert args
        self.args = args

        self.asset_list = list(self.dataset.asset_dict.keys())

        # build in dataframes
        self.weights = pd.DataFrame(columns=self.asset_list)
        self.values = pd.DataFrame(columns=[self.args.strategy_name])
        self.asset_states = pd.DataFrame(columns=self.asset_list, index=['position', 'cost', 'return'])
        self.asset_states.iloc[:,:] = 0

    @abstractmethod
    def generate(self, *args, **kwargs):
        '''
        generate strategy's parameters from 'generation_date_range',
        if the strategy is independ on parameters, then skip this function
        '''
        pass

    @abstractmethod
    def backtestOneDay(self, this_date, *args, **kwargs):
        pass

    def updateValue(self, d):
        if not self.weights.shape[0]:
            self.values.loc[d] = 1
        else:
            self.values.loc[d] = ((self.weights.iloc[-1] * self.asset_daily_yield_df.loc[d]).sum() + (1 - self.weights.iloc[-1].sum())) * self.values.iloc[-1]

            # update asset_states
            self.asset_states.loc['position'] = self.asset_states.loc['position'] * self.asset_daily_yield_df.loc[d]
            self.asset_states.loc['return'] = self.asset_states.loc['position'] / self.asset_states.loc['cost']

    def updateAssetState(self):
        # update asset states 
        target_position = self.weights.iloc[-1] * self.values.iloc[-1]
        for asset in self.asset_list:
            if target_position[asset] < self.asset_states.loc['position', asset]:
                self.asset_states.loc['cost', asset] = self.asset_states.loc['cost', asset] * target_position[asset] / self.asset_states.loc['position', asset]
            else:
                self.asset_states.loc['cost', asset] = self.asset_states.loc['cost', asset] + target_position[asset] - self.asset_states.loc['position', asset]
        self.asset_states.loc['position'] = target_position


    def calculateTransectionCost(self, d):
        target_position = self.weights.iloc[-1] * self.values.iloc[-1].values[0]
        # transection costs

        self.values.loc[d] = self.values.loc[d] - (self.transection_cost * (target_position - self.asset_states.loc['position']).abs()).sum()
        
        
        

    def setDataAndDf(self, date_range):
        # date list with buffer for get raw data
        date_list = self.date_manager.getDateList(date_range, buffer=self.args.buffer)
        self.raw_data, self.missing_date = self.dataset.getData(date_list)
        # date list with buffer for backtest loop
        self.date_list = self.date_manager.getDateList(date_range)
        self.asset_close_df = self.dataset.dict2CloseDf(self.raw_data)
        self.asset_daily_yield_df = self.asset_close_df / self.asset_close_df.shift()



    def run(self, *args, **kwargs):
        '''
        user api
        '''
        self.transection_cost = self.dataset.getTransectionCost()

        # first generate strategy
        if self.args.generation_date_range:
            logging.info('Generating strategy')
            self.setDataAndDf(self.args.generation_date_range)
            self.generate()

        # then do backtest
        logging.info('backtesting')
        self.setDataAndDf(self.args.backtest_date_range)
        transection_date = self.date_manager.getUpdateDateList(self.args.backtest_date_range, frequency=self.args.frequency, missing_date=self.missing_date)
        for i in tqdm(range(len(self.date_list)),
                      desc='backtest', 
                      unit='days'):
            this_date = self.date_list[i]
            # update nav
            self.updateValue(this_date)

            if this_date in transection_date.values and this_date not in self.missing_date:
                # update weights
                self.backtestOneDay(this_date)
                self.updateAssetState()
                self.calculateTransectionCost(this_date)
        self.asset_close_df = self.asset_close_df.loc[self.date_list]

 


        
                



        
