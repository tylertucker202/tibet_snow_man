 # -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 09:57:14 2017

@author: tyler
"""
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import rc
import matplotlib.ticker as mtick
import os
rc('text', usetex=True)
plt.rc('font', family='monospace', size = 20)

colors = ["windows blue", "amber", "greyish", "faded green", "dusty purple"]
#sns.palplot(sns.xkcd_palette(colors))
sns.set_palette(sns.xkcd_palette(colors))

equal_area_filename =  '24_km_false_coverage.csv'
df_ea = pd.read_csv(equal_area_filename)
df_ea.rename(index=str, columns={u'perc coverage': '24_perc_ea', u'coverage (km^2)': '24km_cov_ea'}, inplace = True)
df_ea.index = pd.to_datetime(df_ea['timestamp'], format='%Y-%m-%d')
df_ea = df_ea[df_ea['24km_cov_ea'] != 0] #remove missing data
df_ea.drop(pd.Timestamp('2014-12-03'), inplace=True) #remove outlier
df_ea.drop(pd.Timestamp('2014-12-04'), inplace=True) #remove outlier

filename_24km = '24_km.csv'
df_24 = pd.read_csv(filename_24km)
df_24.rename(index=str, columns={u'perc coverage': '24_perc', u'coverage (km^2)': '24km_cov'}, inplace = True)
df_24.index = pd.to_datetime(df_24['timestamp'], format='%Y-%m-%d')
df_24 = df_24[df_24['24km_cov'] != 0]
df_24.drop(pd.Timestamp('2014-12-03'), inplace=True) #remove outlier
df_24.drop(pd.Timestamp('2014-12-04'), inplace=True) #remove outlier

filename_4km = '4_km.csv'
df_4 = pd.read_csv(filename_4km)
df_4.rename(index=str, columns={'perc coverage': u'4_perc', u'coverage (km^2)': '4km_cov'}, inplace=True)
df_4.index = pd.to_datetime(df_4['timestamp'], format='%Y-%m-%d')
df_4 = df_4[df_4['4km_cov'] != 0] #remove missing data
df_4.drop(pd.Timestamp('2005-02-10'), inplace=True) #remove outlier
#plot 24 and 4

#df.dropna(axis=0, how='any', subset = ['Snow_Area','coverage (km^2)'], inplace=True)


#plot 24 and 4 grids side by side
df_new = pd.concat([df_24,df_4], axis = 1, join = 'inner')

fig1, axes1 = plt.subplots(nrows=2, ncols=1, sharex=True)
df_4['4km_cov'].plot(ax=axes1[0], linewidth = 2)
df_24['24km_cov'].plot(ax=axes1[0], linewidth = 1)
axes1[0].set_title('Timeseries of two resolutions')
axes1[0].set_ylabel(r'Snow coverage, $km^{2}$')
axes1[0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
axes1[0].set_ylim([df_4['4km_cov'].min(),df_4['4km_cov'].max()*1.1])
axes1[0].set_xlabel(r'Date')
axes1[0].legend([r'4x4 $km^{2}$',r'24x24 $km^{2}$'], loc=2)

right_ax1 = axes1[0].twinx()
right_ax1.set_ylim([df_4['4_perc'].min()*100,df_4['4_perc'].max()*100*1.1])
right_ax1.set_ylabel('\%')
right_ax1.grid(False)


tibet_area = 8059061.81949 #calculated via haversine

resolution_perc_diff = 100 * np.divide(np.subtract(df_new['4km_cov'].values,df_new['24km_cov'].values),df_new['24km_cov'].values)
resolution_diff = np.subtract(df_new['4km_cov'].values,df_new['24km_cov'].values)
percent_coverage_difference = 100 * np.divide(np.subtract(df_new['4km_cov'].values,df_new['24km_cov'].values),tibet_area)

df_new['perc_diff'] = percent_coverage_difference
df_new['perc_diff'].plot(ax=axes1[1])
axes1[1].set_title('Percent coverage difference between 4x4 and 24x24 $km^{2}$')
axes1[1].set_ylabel(r'\%')
axes1[1].set_xlabel(r'Date')




#df.dropna(axis=0, how='any', subset = ['Snow_Area','coverage (km^2)'], inplace=True)

#plot old and new

df_ea_and_new = pd.concat([df_ea, df_24], axis = 1, join = 'inner')
fig2, axes2 = plt.subplots(nrows=2, ncols=1, sharex=True)
df_ea_and_new[['24km_cov_ea','24km_cov']].plot(ax=axes2[0])
axes2[0].set_title('Comparison of timeseries')
axes2[0].set_ylabel(r'Snow coverage, $km^{2}$')
axes2[0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
axes2[0].set_ylim([df_ea_and_new['24km_cov_ea'].min(),df_ea_and_new['24km_cov_ea'].max()*1.1])
axes2[0].set_xlabel(r'Date')
axes2[0].legend(['assuming grid = 24x24 $km^{2}$','shoestring formula'], loc=2)

right_ax2 = axes2[0].twinx()
df_ea_and_new[['24_perc_ea','24_perc']].plot(ax=right_ax2)
right_ax2.set_ylabel('\%')
right_ax2.set_ylim([df_ea_and_new['24km_cov_ea'].min()/tibet_area*100,df_ea_and_new['24km_cov_ea'].max()/tibet_area*100*1.1])
right_ax2.grid(False)
right_ax2.legend_.remove()

perc_diff = 100 * np.divide( np.subtract(df_ea_and_new['24km_cov_ea'].values, df_ea_and_new['24km_cov'].values) ,df_ea_and_new['24km_cov'].values)
df_ea_and_new['perc_diff'] = perc_diff
df_ea_and_new['perc_diff'].plot(ax=axes2[1])
axes2[1].set_title('Difference between uniform 24x24 $km^{2}$ assumption vs current method')
axes2[1].set_ylabel(r'\%')
axes2[1].set_xlabel(r'Date')