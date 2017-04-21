# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 14:54:23 2017

@author: tyler
"""
import pandas as pd
from timeseries_analysis import timeseries_report
import matplotlib.pyplot as plt
import os
plt.close('all')

filenames = ['tibet_24_km.csv',
             'Alberta-24km.csv',
             'Alps-24km.csv',
             'Artic-24km.csv',
             'Sierras-24km.csv']


for filename in filenames:
    
    series_name = filename.strip('_km.csv').replace('_','-')
    outlier_dates = []
    df = pd.read_csv(filename, index_col='timestamp')
    
    ts_report = timeseries_report(series_name,df, outlier_dates)
    #plt.show('all')
    raw_input("Press Enter to continue...")
    plt.close('all')
    