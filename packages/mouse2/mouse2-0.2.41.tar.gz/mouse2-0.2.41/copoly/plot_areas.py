#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon May 26 22:55:24 2025

@author: misha
"""

import sys
import math
from matplotlib import pyplot as plt

R = 1.
NORM = 4. * math.pi * R**2
XLABEL = "n"
YLABEL = "Доля доступной растворителю поверхности звеньев ВИ"

lines = sys.stdin.readlines()
for line in lines:
    if line.startswith("VI mean"):
        data = eval(line[9:])
        data = dict(data)
        data_list = []
        for x in data.keys():
            data_list.append((x, data[x]))
        data_list.sort()
        x_list = list([i[0] for i in data_list])
        y_list = list([i[1]/NORM for i in data_list])
        plt.plot(x_list, y_list)
        plt.xlabel(XLABEL)
        plt.ylabel(YLABEL)
        plt.legend()
        plt.show()
