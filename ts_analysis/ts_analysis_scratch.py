# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 19:39:51 2017

@author: tyler
"""

import pandas as pd
import os
import numpy as np
homeDir = os.getcwd()
filename_24km = 'tibet_24_km.csv'


df_24 = pd.read_csv(filename_24km, index_col='timestamp')
df_24.rename(index=str, columns={u'perc coverage': '24_perc', u'coverage (km^2)': '24km_cov'}, inplace = True)
df_24.index = pd.to_datetime(df_24.index, format='%Y-%m-%d')
#df_24.index = pd.to_datetime(df_24.index, format='%j')
df_24 = df_24[df_24['24km_cov'] != 0] #removes bad dates
df_24.drop(pd.Timestamp('2014-12-03'), inplace=True) #remove outlier
df_24.drop(pd.Timestamp('2014-12-04'), inplace=True) #remove outlier


#reindex to include all days
idx = pd.date_range(df_24.index.min(), df_24.index.max())

df_re = df_24.reindex(idx, fill_value = np.NaN)
df_re = df_re[~((df_re.index.month == 2) & (df_re.index.day == 29))] #remove leapdays
#index = df_re[df_re['timestamp'] == -999].index
index = df_re[df_re[df_re.columns[0]] == -999].index

agg_5d = df_re.groupby(pd.TimeGrouper(freq='5D')).aggregate(len)
agg_5d2 = df_24.groupby(pd.TimeGrouper(freq='5D')).aggregate(len)

#testing

test_ts = pd.date_range('1997-02-04', periods=30, freq='D')
df_test= df_24.reindex(test_ts)
df_test.drop(pd.Timestamp('1997-02-15'), inplace=True)
agg_test = df_test.groupby(pd.TimeGrouper(freq='5D')).aggregate(len)

test_ts_ly = pd.date_range('2000-02-04', periods=30, freq='D')
df_test_ly= df_24.reindex(test_ts_ly)
df_test_ly.drop(pd.Timestamp('2000-02-15'), inplace=True)
df_test_ly = df_test_ly[~((df_test_ly.index.month == 2) & (df_test_ly.index.day == 29))]
agg_test_ly = df_test_ly.groupby(pd.TimeGrouper(freq='5D')).aggregate(len)

df_re.head(20)

test_ts[0].dayofyear


#
y = pd.date_range('1999-01-01', '1999-12-31').dayofyear.reshape(73,5)
ly = pd.date_range('2000-01-01', '2000-12-31').drop(pd.Timestamp('2000-02-29')).dayofyear.reshape(73,5)

bin_function = lambda x: df_24[ df_24['dayofyear'].isin(x)]
bin_maps = map(bin_function, y)

rowSums = map(lambda x: x.sum(),bin_maps)
rowMean = map(lambda x: x.mean(),bin_maps)
rowStd = map(lambda x: x.std(),bin_maps)
rowCounts = map(lambda x: x.count(),bin_maps)

df_24['dayofyear'] = df_24.index.dayofyear
df_24[ df_24['dayofyear'].isin(y[0])]


##adding columns used to get yearly averages
#df_24['dayofyear'] = df_24.index.dayofyear
#is_leap_year = lambda x: x.year % 4 == 0
#df_24['is_leap_year'] = map(is_leap_year, df_24.index)
#
##split into leap years and non leap years.
#df_24_ly = df_24[df_24['is_leap_year'] == True]
#df_24_y = df_24[df_24['is_leap_year'] == False]
#
#
##make timeseries with periods of every 5 days
#
#period = 12
#n_rows = 365/period
##todo: make so that you dont have this be a factor of of 365
#
#y = np.array_split(pd.date_range('1999-01-01', '1999-12-31').dayofyear, n_rows)
#ly = np.array_split(pd.date_range('2000-01-01', '2000-12-31').drop(pd.Timestamp('2000-02-29')).dayofyear, n_rows)
#
##group dataframes into 5 day periods
#bin_function_y = lambda x: df_24_y[ df_24_y['dayofyear'].isin(x)]
#bin_maps_y = map(bin_function_y, y)
#
##leap days have different days of the year after feb 2nd. 
#bin_function_ly = lambda x: df_24_ly[ df_24_ly['dayofyear'].isin(x)]
#bin_maps_ly = map(bin_function_ly, ly)
#
##add each group together
#concat_bins = lambda x: pd.concat([bin_maps_ly[x], bin_maps_y[x]])
#bin_maps = map(concat_bins, np.arange(0,n_rows))
#
##collect parameters
#rowSums = map(lambda x: x['24km_cov'], map(lambda x: x.sum(),bin_maps))
#rowMean = map(lambda x: x['24km_cov'], map(lambda x: x.mean(),bin_maps))
#rowStd = map(lambda x: x['24km_cov'], map(lambda x: x.std(),bin_maps))
#rowCounts = map(lambda x: x['24km_cov'], map(lambda x: x.count(),bin_maps))
#
##create dataframe to house parameters for each 5 day period
#df_bin = pd.DataFrame()
#df_bin['days'] = map(lambda x: str(x[0])+'-'+str(x[-1]),y)
#df_bin['sums'] = rowSums
#df_bin['mean'] = rowMean
#df_bin['std'] = rowStd
#df_bin['counts'] = rowCounts
#df_bin['dayofyear'] = map(lambda x: x[0],y)


#df_24['timestamp']=df_24.index.to_series()
#
#df_test = df_test.append([df_test]*(period-1),ignore_index=True)
#df_test.sort_values(by='first_day', inplace=True)
#df_test['dayofyear'] = np.arange(1,366)
#df_out = pd.merge(df_24, df_test, on='dayofyear', how='inner')
#df_out.index = df_out['timestamp']
#
#df_out.sort_index(inplace=True)
#df_out.drop(['is_leap_year', 'first_day', 'days', '24_perc', 'sums', 'timestamp'], axis = 1, inplace=True)
#

