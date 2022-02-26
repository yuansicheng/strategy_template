#!/usr/bin/python
# -*- coding: utf-8 -*-

# @Author	:	yuansc
# @Contact	:	yuansicheng@ihep.ac.cn
# @Date		:	2022-02-24 

import os, sys, argparse, logging
import re

class ArgManager():
    def __init__(self) -> None:
        parser = argparse.ArgumentParser()
        self.args = parser.parse_args()

    def loadArgsFromFile(self, filename):
        parser = argparse.ArgumentParser()
        args = parser.parse_args()

        arg_group_name = os.path.basename(filename).split('.')[0]

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.replace('\n', '').strip()
            # skip comments
            if re.match('^[#$].*', line):
                continue
            if '=' not in line:
                continue

            line_split = line.split('=')
            arg_key = line_split[0].strip()
            arg_value = line_split[1].strip()

            if re.match('^\d+$', arg_value):
                arg_value = int(arg_value)
            elif re.match('^\d+\.\d+$', arg_value):
                arg_value = float(arg_value)
            else:
                pass

            setattr(args, arg_key, arg_value)
            logging.info('Set {}.{} = {}'.format(arg_group_name, arg_key, arg_value))

        setattr(self.args, arg_group_name, args)

# # test
# arg_manager = ArgManager()
# arg_manager.loadArgsFromFile('scripts/base_classes/constants.txt')
# print(arg_manager.args.constants.RFR)

