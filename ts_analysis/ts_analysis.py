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
           "axes.labelsize":22,
           'xtick.labelsize':16,
           'ytick.labelsize':16}

sns.set_context("paper", rc=rcStyle) 
from scipy import stats
from scipy import signal

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
df_out['diff'] = (df_out['24km_cov']-df_out['mean'])
df_out['timestamp'] = df_out.index
df_out['timestamp'] = pd.to_datetime(df_out['timestamp'], format='%Y-%m-%d').astype(int).astype(float).values



#time series analysis
#time series trendline
y=df_out['diff']/((10**3)**2) #build a trendline from non-parametric model.
#y=df_out['z'].values #build a trendline from standardized model

x=df_out['timestamp']
ts_line = pd.ols(y=y, x=x, intercept = True)
#print(ts_line.summary)
trend = ts_line.predict(beta=ts_line.beta, x=x) 
data = pd.DataFrame(index=df_out.index, data={'y': y, 'trend': trend})


slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

print('Linear Regression Results \n slope: {0} \n intercept: {1} \n r-value: {2} \n p-value: {3} \n std_err: {4}'.format(slope, intercept, r_value, p_value, std_err))




fig0 = plt.figure(0)
axes0 = plt.axes()
axes0.plot(x.index.values, y.values, linewidth = 2)
axes0.plot(x.index.values, data['trend'].values, linewidth = 2)
axes0.set_title('Time Series of Snow Cover Anomalies')
axes0.set_ylabel(r'Anomalies, $Mm^2$')
axes0.set_xlabel(r'Date')
#axes0.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
axes0.set_xlim([x.index.min(),x.index.max()])

plt.savefig('tibet_24_averaged.png')



#save csv's and plots
df_bin.to_csv('annual_expected_coverage.csv')
df_out.to_csv('tibet_24_averaged.csv')

fig1 = plt.figure(1)
axes1 = plt.axes()
axes1.plot(df_bin['first_day'].values,df_bin['mean'].values, linewidth = 2)
#df_bin['mean'].plot(ax = axes1, linewidth = 2)
axes1.set_title('Timeseries of 5 day averages')
axes1.set_ylabel(r'Mean snow coverage, $km^2$')
axes1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
axes1.set_xlabel(r'Day of year')
axes1.set_xlim([df_bin['first_day'].min(),df_bin['first_day'].max()])
plt.savefig('tibet_24_anomolies_ts.png')

fig2 = plt.figure(2)
axes2 = plt.axes()
axes2.hist(y,60)
#df_bin['mean'].plot(ax = axes1, linewidth = 2)
axes2.set_title('Histogram of anomalies')
axes2.set_ylabel(r'Counts')
axes2.set_xlabel(r'Snow anomolies, $Mm^2$')
#axes2.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
plt.savefig('tibet_24_anomolies_hist.png')

#power spectrum plot
fs = 1 #day
f, Pxx_den = signal.periodogram(y, fs)
#f, Pxx_den = signal.periodogram(df_24['24km_cov'].values, fs)
fig3 = plt.figure(3)
axes3 = plt.axes()

#t = 1/f 
df_24['24km_cov']
axes3.semilogy(f*365, Pxx_den)
#axes3.set_ylim([1e-3, 10e7])
#axes3.set_ylim([10e5, 10e14])
axes3.set_title('Power spectrum of anomalies')
axes3.set_xlabel('frequency [1/year]')
axes3.set_ylabel('Power')
plt.savefig('tibet_24_anomolies_spectral_power_denstiy.png')




