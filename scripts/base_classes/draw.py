#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.set_loglevel("info") 

def drawWeights(weights, fig_name):
    # draw weights
    plt.cla()
    plt.figure(figsize=(16,4), dpi=256)
    ax = plt.axes()
    weights.plot.area(ax=ax)
    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
    plt.title('Historical Weights')
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close()


def drawValues(values, fig_name, asset_close_df=None, benchmark=None):
    # draw values
    plt.cla()
    plt.figure(figsize=(16,4), dpi=256)
    ax = plt.axes()
    values.plot(ax=ax, zorder=1000, color='black', linewidth=2)
    if not benchmark is None:
        benchmark.plot(ax=ax, zorder=500, linewidth=2, style='--')
    if not asset_close_df is None:
        asset_close_df /= asset_close_df.iloc[0]
        asset_close_df.plot(ax=ax, zorder=100, linewidth=1, alpha=0.6)
    plt.grid()
    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
    plt.title('Historical Values')
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close()
