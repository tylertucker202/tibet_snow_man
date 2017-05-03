# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 13:58:23 2017

@author: tyler
"""

import matplotlib.pyplot as plt
import pandas as pd
#%matplotlib inline
import pdb
import seaborn as sns
from matplotlib import rc
import datetime
import matplotlib.ticker as mtick
rc('text', usetex=True)
rcStyle = {"font.size":22,
           "axes.titlesize":22,
           "axes.labelsize":22,
           'xtick.labelsize':16,
           'ytick.labelsize':16}
sns.set_context("paper", rc=rcStyle) 
colors = ["windows blue", "amber", "scarlet", "faded green", "dusty purple"]
sns.set_palette(sns.xkcd_palette(colors))
from scipy import stats
from scipy import signal

import os
import numpy as np

class timeseries_report:
    """
    creates climate averaged table and stats info
    """
    def __init__(self,series_name,df, outlier_dates):
        
        self.series_name = series_name #used when saving files
        
        df.rename(index=str, columns={u'coverage (km^2)': 'coverage'}, inplace = True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')

        df = df[df['coverage'] != 0] #removes bad dates
        
        df = df[~((df.index.month == 2) & (df.index.day == 29))] #remove leap days
        
        for date in outlier_dates:
            df.drop(pd.Timestamp(date), inplace=True) #remove outliers
        self.df = df
        self.clim = self.get_climate_df(period = 5)
        self.df_out = self.merge_df()
        self.make_anomalies()
        
        self.make_yearly_mean()
        self.do_stats()
        
        #start saving and plotting
        self.save_data()
        
        #self.make_timeseries_plot()
        self.make_timeseries_subplot() #better to use a subplot
        self.make_climate_plot()
        self.make_histogram()
        self.make_spectrum()
        
    def save_data(self):
        #save csv's and plots
        if not os.path.exists(self.series_name):
            os.mkdir(self.series_name)
        self.clim.to_csv(os.path.join(self.series_name,self.series_name+'-annual_expected_coverage.csv'))
        self.df_out.to_csv(os.path.join(self.series_name,self.series_name+'-averaged.csv'))
        
        
    def get_climate_df(self, period = 5):
        #adding columns used to get yearly averages
        df=self.df
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
        climate_function_y = lambda x: df_y[ df_y['dayofyear'].isin(x)]
        climate_maps_y = map(climate_function_y, y)
        
        #leap days have different days of the year after feb 2nd. 
        climate_function_ly = lambda x: df_ly[ df_ly['dayofyear'].isin(x)]
        climate_maps_ly = map(climate_function_ly, ly)
        
        #add each group together
        concat_climates = lambda x: pd.concat([climate_maps_ly[x], climate_maps_y[x]])
        climate_maps = map(concat_climates, np.arange(0,n_rows))
        
        #collect parameters
        rowSums = map(lambda x: x['coverage'], map(lambda x: x.sum(),climate_maps))
        rowMean = map(lambda x: x['coverage'], map(lambda x: x.mean(),climate_maps))
        rowStd = map(lambda x: x['coverage'], map(lambda x: x.std(),climate_maps))
        rowCounts = map(lambda x: x['coverage'], map(lambda x: x.count(),climate_maps))
        
        #create dataframe to house parameters for each 5 day period
        df_climate = pd.DataFrame()
        df_climate['days'] = map(lambda x: str(x[0])+'-'+str(x[-1]),y)
        df_climate['first_day'] = map(lambda x: x[0],y)
        df_climate['sums'] = rowSums
        df_climate['mean'] = rowMean
        df_climate['std'] = rowStd
        df_climate['counts'] = rowCounts
        df_climate['dayofyear'] = map(lambda x: x[0],y)
        
        return df_climate
        
    def merge_df(self,period=5):
        """
        does a tricky merge involving a group on day of year. 
        1. append data for the df_climate so that it has the same length as df
        2. inner merge on dayofyear
        3. drop replicated columns
        """
        self.df['timestamp']=self.df.index.to_series()
        if not period ==1:
            self.clim = self.clim.append([self.clim]*(period-1),ignore_index=True)
        self.clim.sort_values(by='first_day', inplace=True)
        self.clim['dayofyear'] = np.arange(1,366)
        df_out = pd.merge(self.df, self.clim, on='dayofyear', how='inner')
        df_out.index = df_out['timestamp']
        df_out.sort_index(inplace=True)
        df_out.drop(['is_leap_year', 'first_day', 'days', 'perc coverage', 'sums', 'timestamp'], axis = 1, inplace=True)
    
        return df_out
    
    def make_anomalies(self):
        self.df_out['z'] = (self.df_out['coverage']-self.df_out['mean'])/self.df_out['std']
        self.df_out['perc_diff'] = 100*(self.df_out['coverage']-self.df_out['mean'])/self.df_out['mean']
        self.df_out['anom'] = (self.df_out['coverage']-self.df_out['mean'])
        self.df_out['timestamp'] = self.df_out.index
        self.df_out['timestamp'] = pd.to_datetime(self.df_out['timestamp'], format='%Y-%m-%d').astype(int).astype(float).values

    def make_yearly_mean(self):
        """
        bins data into years and takes the average
        """
        #used for yearly binning
        grouped = self.df_out.groupby(lambda x: x.year)
        self.yearly_anom_mean = grouped['anom'].mean()
        years = map(lambda x: str(x), self.yearly_anom_mean.index.values)
        years = map(lambda x: datetime.datetime.strptime(x, '%Y'), years)
        self.yearly_anom_mean.index = years

        
    def do_stats(self):
        
        with open(os.path.join(self.series_name,self.series_name+'-report-stats.txt'), 'w') as f:
            
            f.write('\n\n============\n'+self.series_name+'=================\n')
            f.write('Climate averaged properties [10^6 km^2] \n max: {0}: \n min: {1} \n'.format(self.clim['mean'].max()/10**6,self.clim['mean'].min()/10**6) )
    
            #time series trendline
        
            
            self.anomalies=self.df_out['anom']/(10**6) #build a trendline from non-parametric model.
            #y=df_out['z'].values #build a trendline from standardized model
            
            self.timestamps=self.df_out['timestamp']
            ts_line = pd.ols(y=self.anomalies, x=self.timestamps, intercept = True)
            trend = ts_line.predict(beta=ts_line.beta, x=self.timestamps) 
            self.trendline_data = pd.DataFrame(index=self.df_out.index, data={'y': self.anomalies, 'trend': trend})
            
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(self.timestamps,self.anomalies)
            
            f.write('Linear Regression Results \n slope: {0} \n intercept: {1} \n r-value: {2} \n p-value: {3} \n std_err: {4} \n'.format(slope, intercept, r_value, p_value, std_err))
            
            f.write('Anomaly distribution results \n mean: {0}: \n std: {1} \n skew: {2} \n kurtosis: {3} \n'.format(self.df_out['anom'].mean(),self.df_out['anom'].std(),self.df_out['anom'].skew(),self.df_out['anom'].kurtosis()))
            
            skew_test = stats.skewtest(self.df_out['anom'].values)
            kurt_test = stats.kurtosistest(self.df_out['anom'].values)
            
            f.write(' kurtosis test p-value: {0} \n skew test p-value: {1}'.format(round(kurt_test.pvalue,3), round(skew_test.pvalue,3)))

    def make_timeseries_plot(self):
        """
        superimposes barchart: currently not being used
        """
        fig0 = plt.figure(0,figsize=(7.8,5.7))
        #fig0.set_figheight(5)
        #fig0.set_figwidth(7.4)
        axes0 = plt.axes()
        axes0.plot(self.timestamps.index.values, self.anomalies.values, linewidth = 2, alpha = 1)
        
        axes0.plot(self.timestamps.index.values, self.trendline_data['trend'].values, linewidth = 2)
        axes0.set_title(self.series_name+': Time Series of Snow Cover Anomalies')
        axes0.set_ylabel(r'Anomalies [$10^{6} km^{2}$]')
        #axes0.set_ylim([self.yearly_anom_mean.values.min()*1.1/10**5,self.anomalies.max()*1.1])

        axes0.set_xlabel(r'Date')
        axes0.set_xlim([self.timestamps.index.min(),self.timestamps.index.max()])
        
        axes0.bar(self.yearly_anom_mean.index.values, self.yearly_anom_mean.values/10**5, color='w',width=365)
        axes0_2 = axes0.twinx()
        axes0_2.set_ylim([-2,2.5])
        axes0_2.set_ylabel('Yearly avg. anomalies [$10^{5} km^{2}$]')
        axes0_2.grid(False)
        axes0.legend([r'time series',
                         r'trendline', 'yr. avg.'],
                         frameon = True)
        plt.savefig(os.path.join(self.series_name,self.series_name+'-averaged.png'),bbox_inches='tight')
    
    def make_timeseries_subplot(self):
        fig0, axes0 = plt.subplots(2,1,figsize=(7.8,5.7), sharex = True)
        axes0[0].plot(self.timestamps.index.values, self.anomalies.values, linewidth = 2, alpha = 1)
        
        axes0[0].plot(self.timestamps.index.values, self.trendline_data['trend'].values, linewidth = 2)
        axes0[0].set_title(self.series_name+': Time Series of Snow Cover Anomalies')
        axes0[0].set_ylabel(r'Anom. [$10^{6} km^{2}$]')
        #axes0[0].set_ylim([-2,2.5])
        axes0[0].set_xlim([self.timestamps.index.min(),self.timestamps.index.max()])
        
        axes0[1].bar(self.yearly_anom_mean.index.values, self.yearly_anom_mean.values/10**5, color='w',width=365)
        axes0_L = axes0[1].twinx()
        #axes0[1].set_ylim([-2,2.5])
        axes0_L.set_ylabel('Yearly avg. anom. [$10^{5} km^{2}$]')
        axes0_L.yaxis.set_ticks([])
        axes0_L.yaxis.set_label_coords(1.03,.8)
        axes0[1].grid(False)
        axes0[1].set_xlabel(r'Date')
        axes0[0].legend([r'time series',
                 r'trendline'],
                 frameon = True)
        plt.savefig(os.path.join(self.series_name,self.series_name+'-averaged.png'),bbox_inches='tight')
        
    def make_climate_plot(self):
        fig1 = plt.figure(1)
        axes1 = plt.axes()
        axes1.plot(self.clim['first_day'].values,self.clim['mean'].values/(10**6), linewidth = 2)
        #clim['mean'].plot(ax = axes1, linewidth = 2)
        axes1.set_title(self.series_name+': Time Series of 5 Day Averages')
        axes1.set_ylabel(r'Mean snow coverage [$10^{6} km^{2}$]')
        axes1.set_xlabel(r'Day of year')
        axes1.set_xlim([self.clim['first_day'].min(),self.clim['first_day'].max()])
        plt.savefig(os.path.join(self.series_name,self.series_name+'-24-anomalies-ts.png'),bbox_inches='tight')
        
    def make_histogram(self):
        fig2 = plt.figure(2)
        axes2 = plt.axes()
        axes2.hist(self.anomalies,60)
        #clim['mean'].plot(ax = axes1, linewidth = 2)
        axes2.set_title(self.series_name+': Histogram of Anomalies')
        axes2.set_ylabel(r'Counts')
        axes2.set_xlabel(r'Snow anomolies [$10^{6} km^{2}]$')
        #axes2.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.e'))
        plt.savefig(os.path.join(self.series_name,self.series_name+'-anomalies-hist.png'),bbox_inches='tight')
    
    def make_spectrum(self):
        #power spectrum plot
        fs = 1 #day
        f, Pxx_den = signal.periodogram(self.anomalies, fs)
        fig3 = plt.figure(3)
        axes3 = plt.axes()
        axes3.semilogy(f*365, Pxx_den)
        axes3.set_xlim([0, 20])
        axes3.set_ylim([10e-6, 10e1])
        axes3.set_title(self.series_name+': Power Spectrum of Snow Cover Anomalies')
        axes3.set_xlabel('Frequency [1/day]')
        axes3.set_ylabel('Power [$(10^{6} km^{2})^{2}/(1/day)$]')
        plt.savefig(os.path.join(self.series_name,self.series_name+'-anomalies-spectral-power-denstiy.png'),bbox_inches='tight')