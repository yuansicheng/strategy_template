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
        std = self.asset_daily_yield_df.loc[:this_date].iloc[-self.args.constants.DAY_OF_YEAR:].std()
        self.weights.loc[this_date] = (1/std) / (1/std).sum()


