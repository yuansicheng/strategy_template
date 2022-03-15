#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging

import pandas as pd
from datetime import datetime
from glob import glob

from rp_strategy import RP
from base_classes.arg_manager import ArgManager
from base_classes.dataset import Dataset
from base_classes.evaluator import Evaluator
from base_classes.benchmark import Benchmark
from base_classes.draw import *
from base_classes.date_manager import DateManager

os.chdir(os.path.dirname(os.path.abspath(__file__)))

debug = False
# set loglevel
if debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO
logging.basicConfig(level=loglevel, format="%(asctime)s-%(filename)s[line:%(lineno)d]-%(funcName)s-%(levelname)s : %(message)s")

####################################################
####################################################
arg_manager = ArgManager()
# load constants
arg_manager.loadArgsFromFile('base_classes/constants.txt')
args = arg_manager.args
# args
args.strategy_name = 'rp'
args.frequency = 'quarterly'
args.rebalance_frequency = 'monthly'
args.generation_date_range = []
args.backtest_date_range = [datetime(2010, 1, 1), datetime(2020, 12, 31)]
args.result_path = '../result'
args.buffer = args.constants.DAY_OF_YEAR

####################################################
####################################################
# set asset
dataset = Dataset()
# set weight constraint for 'root' group (all assets)
dataset.group.weight_range = [0., 1.]
# Precise assignment
dataset.addGroup(group='bonds', weight_range=[0.3, 0.9])
dataset.addAsset('../data/中债-国债总财富(总值)指数.csv', transection_cost=0.001, group='bonds', weight_range=[0., 0.9])
dataset.addAsset('../data/中债-信用债总财富(总值)指数.csv', transection_cost=0.001, group='bonds', weight_range=[0., 0.9])

dataset.addGroup(group='stocks', weight_range=[0.1, 0.6])
dataset.addAsset('../data/沪深300指数(全收益).csv', transection_cost=0.002, group='stocks', weight_range=[0., 0.6])
dataset.addAsset('../data/上证50(全收益).csv', transection_cost=0.002, group='stocks', weight_range=[0., 0.6])

# Fuzzy assignment
files = glob('../data/*黄金*')
for asset_file in files:
    dataset.addAsset(asset_file, transection_cost=0.003, weight_range=[0.1, 0.5])

# print current dataset
dataset.printGroup(dataset.group)
####################################################
####################################################
# set benchmark
benchmark = Benchmark(benchmark_name='benchmark: 0.7x国债+0.3x沪深300')
benchmark.addAsset('../data/中债-国债总财富(总值)指数.csv', 0.7)
benchmark.addAsset('../data/沪深300指数(全收益).csv', 0.3)
####################################################
####################################################

date_manager = DateManager('base_classes/transection_date.csv')

date_list = date_manager.getDateList(args.backtest_date_range)
benchmark_value = benchmark.getValue(date_list)


rp = RP(dataset=dataset,
        date_manager=date_manager,
        args=args)
rp.run()

# save and draw
rp.weights.to_csv(os.path.join(args.result_path, 'weights.csv'))
drawWeights(rp.weights, rp.marked_date, os.path.join(args.result_path, 'weights.png'))

rp.values.to_csv(os.path.join(args.result_path, 'values.csv'))
drawValues(rp.values, os.path.join(args.result_path, 'values.png'), asset_close_df=rp.asset_close_df, benchmark=benchmark_value)


evaluation = Evaluator(strategy_value=rp.values, benchmark_value = benchmark_value, asset_close_df=rp.asset_close_df, args=args.constants).evaluate()
# set encoding='utf_8_sig' to show Chinese
evaluation.to_csv(os.path.join(args.result_path, 'evaluation.csv'), encoding='utf_8_sig')

