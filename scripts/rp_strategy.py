#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-05

import os
import sys
import argparse
import logging

from base_classes.strategy import Strategy


class RP(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        

    def generate(self):
        pass

    def backtestOneDay(self, this_date):
        if this_date in self.transection_date:
            std = self.asset_daily_yield_df.loc[:this_date].iloc[-self.args.constants.DAY_OF_YEAR:].std()
            self.weights.loc[this_date] = (1/std) / (1/std).sum()
            self.marked_date['update'].append(this_date)
            return
        if self.weights.shape[0] and this_date in self.rebalance_date:
            # do rebalance
            if not self.marked_date['update']:
                return
            self.weights.loc[this_date] = self.weights.loc[self.marked_date['update'][-1]]
            self.marked_date['rebalance'].append(this_date)
            return


