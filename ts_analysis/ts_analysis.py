# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 19:39:51 2017

@author: tyler
"""


import matplotlib.pyplot as plt

import pandas as pd
#%matplotlib inline

import pdb
import seaborn as sns
from matplotlib import rc

import matplotlib.ticker as mtick
rc('text', usetex=True)
rcStyle = {"font.size":22,
           "axes.titlesize":22,
           "axes.labelsize":16,
           'xtick.labelsize':12,
           'ytick.labelsize':12}

sns.set_context("paper", rc=rcStyle) 

import os
import numpy as np
homeDir = os.getcwd()
filename_24km = 'tibet_24_km.csv'

#load and format file
df_24 = pd.read_csv(filename_24km, index_col='timestamp')
df_24.rename(index=str, columns={u'perc coverage': '24_perc', u'coverage (km^2)': '24km_cov'}, inplace = True)
df_24.index = pd.to_datetime(df_24.index, format='%Y-%m-%d')


#removing outliers and leap days
df_24 = df_24[df_24['24km_cov'] != 0] #removes bad dates
df_24.drop(pd.Timestamp('2014-12-03'), inplace=True) #remove outlier
df_24.drop(pd.Timestamp('2014-12-04'), inplace=True) #remove outlier
df_24 = df_24[~((df_24.index.month == 2) & (df_24.index.day == 29))] #remove leap days

def get_period_df(df, period = 5):
    #adding columns used to get yearly averages
    df['dayofyear'] = df.index.dayofyear
    is_leap_year = lambda x: x.year % 4 == 0
    df['is_leap_year'] = map(is_leap_year, df.index)
    
    #split into leap years and non leap years.
    df_ly = df[df['is_leap_year'] == True]
    df_y = df[df['is_leap_year'] == False]
    
    
    #make timeseries with periods of every n days
    n_rows = int(np.floor(365/period))
    #todo: make so that you dont have this be a factor of of 365
    
    y = np.array_split(pd.date_range('1999-01-01', '1999-12-31').dayofyear, n_rows)
    ly = np.array_split(pd.date_range('2000-01-01', '2000-12-31').drop(pd.Timestamp('2000-02-29')).dayofyear, n_rows)
    
    #group dataframes into 5 day periods
    bin_function_y = lambda x: df_y[ df_y['dayofyear'].isin(x)]
    bin_maps_y = map(bin_function_y, y)
    
    #leap days have different days of the year after feb 2nd. 
    bin_function_ly = lambda x: df_ly[ df_ly['dayofyear'].isin(x)]
    bin_maps_ly = map(bin_function_ly, ly)
    
    #add each group together
    concat_bins = lambda x: pd.concat([bin_maps_ly[x], bin_maps_y[x]])
    bin_maps = map(concat_bins, np.arange(0,n_rows))
    
    #collect parameters
    rowSums = map(lambda x: x['24km_cov'], map(lambda x: x.sum(),bin_maps))
    rowMean = map(lambda x: x['24km_cov'], map(lambda x: x.mean(),bin_maps))
    rowStd = map(lambda x: x['24km_cov'], map(lambda x: x.std(),bin_maps))
    rowCounts = map(lambda x: x['24km_cov'], map(lambda x: x.count(),bin_maps))
    
    #create dataframe to house parameters for each 5 day period
    df_bin = pd.DataFrame()
    df_bin['days'] = map(lambda x: str(x[0])+'-'+str(x[-1]),y)
    df_bin['first_day'] = map(lambda x: x[0],y)
    df_bin['sums'] = rowSums
    df_bin['mean'] = rowMean
    df_bin['std'] = rowStd
    df_bin['counts'] = rowCounts
    df_bin['dayofyear'] = map(lambda x: x[0],y)    
    
    return df_bin

def merge_df(df, df_bin,period):

    df['timestamp']=df.index.to_series()
    if not period ==1:
        df_bin = df_bin.append([df_bin]*(period-1),ignore_index=True)
    df_bin.sort_values(by='first_day', inplace=True)
    df_bin['dayofyear'] = np.arange(1,366)
    df_out = pd.merge(df, df_bin, on='dayofyear', how='inner')
    df_out.index = df_out['timestamp']
    df_out.sort_index(inplace=True)
    df_out.drop(['is_leap_year', 'first_day', 'days', '24_perc', 'sums', 'timestamp'], axis = 1, inplace=True)

    return df_out

period = 5
df_bin = get_period_df(df_24, period)

df_out = merge_df(df_24, df_bin, period)

get_z_values = lambda x: (x['24km_cov']-x['mean'])/x['std']
df_out['z'] = (df_out['24km_cov']-df_out['mean'])/df_out['std']
df_out['perc_diff'] = 100*(df_out['24km_cov']-df_out['mean'])/df_out['mean']

#time series analysis

fig = plt.figure(0)
axes = plt.axes()
df_out['perc_diff'].plot(linewidth = 2)
axes.set_title('Timeseries of two resolutions')
axes.set_ylabel(r'Snow anomolies, \%')
axes.set_xlabel(r'date')
axes.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))


df_out['timestamp'] = df_out.index
df_out['timestamp'] = pd.to_datetime(df_out['timestamp'], format='%Y-%m-%d').astype(int).astype(float).values
y=df_out['perc_diff']
#y=df_out['z'].values

x=df_out['timestamp']

ts_line = pd.ols(y=y, x=x, intercept = True)
print(ts_line.summary)
trend = ts_line.predict(beta=ts_line.beta, x=x) 
data = pd.DataFrame(index=df_out.index, data={'y': y, 'trend': trend})
data['trend'].plot(linewidth = 2)
#axes.set_xlim([df_new.index.min(),df_new.index.max()])

from scipy import stats
import numpy as np
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print('Linear Regression Results \n slope: {0} \n intercept: {1} \n r-value: {2} \n p-value: {3} \n std_err: {4}'.format(slope, intercept, r_value, p_value, std_err))

#save csv's and plots
df_bin.to_csv('annual_expected_coverage.csv')
df_out.to_csv('tibet_24_averaged.csv')
plt.savefig('tibet_24_averaged.png')





