# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 17:00:35 2016

@author: tyler
"""
import os, glob
import gzip
import pdb
import numpy as np
import re
import matplotlib.pyplot as plt
import pandas as pd
#import matplotlib
import logging
from mpl_toolkits.basemap import Basemap, cm
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata
#plt.ioff()

class makeSnowDF:
    def __init__(self,code_dir,lat_long_filename,lat_long_coords):
        logging.debug('initializing object')
        self.code_dir = code_dir
        self.logic_matrix = np.matrix([ [1, 1, 1, 1, 1 ], #row: x is reporting space
                                 [0, 1, 0, 1, 0 ], #x is reporting water
                                 [0, 0, 1, 0, 1 ], #x is reporting land
                                 [1, 1, 1, 1, 1 ], #x is reporting ice
                                 [1, 1, 1, 1, 1 ]] )#x is reporting snow
        self.coords = lat_long_coords
        self.lat_long_filename = lat_long_filename
        self.df = pd.read_csv(self.code_dir+self.lat_long_filename, index_col=(0,1))
            
    def computeMonthlyAverage(self,input_df):        
        days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        days_per_month_ly = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]        
        cum_days = {}
        cum_days[0] = 0
        cum_days_ly = {}
        cum_days_ly[0] = 0
                
        col_bins = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}
        #col_bins = {'jan':[], 'feb':[], 'mar':[], 'april':[], 'may':[], 'june':[], 'july':[], 'aug':[], 'sept':[], 'oct':[], 'nov':[], 'dec':[]}
        
        #only snow and ice are captured
        def snow_and_ice(x):
            if x==4 or x==3:
                x=1 
            else: 
                x=0
            return x
            
        #only consider snow and ice over areas. 
        #pdb.set_trace()
        input_df = input_df.applymap(snow_and_ice)  
        
        for month, days in enumerate(days_per_month):
            cum_days[month+1] = cum_days[month] + days_per_month[month]
            cum_days_ly[month+1] = cum_days_ly[month] + days_per_month_ly[month]
        cum_days.popitem() #removes 0th month
        cum_days_ly.popitem() #removes 0th month
        #print ('cumulative days:{}'.format(cum_days))
        #print ('cumulative leapyear days:{}'.format(cum_days_ly))
        #loop over columns

        for col in input_df.columns:
            year, day = col.split('_')
            year = int(year)
            day = int(day)
        
            if year%4 == 0: #use leapyear 
                month_bin = cum_days_ly
                days_in_month = days_per_month_ly
            elif year%4 != 0:
                month_bin = cum_days
                days_in_month = days_per_month
            #determine which month bin day belongs.
            
            try:
                my_list = map(lambda x: x - day, month_bin.values())
                my_month = my_list.index(min(x for x in my_list if x >= 0))+1
                col_bins[my_month].append(col)
            except ValueError as err:
                print('value error found: {0}'.format(err))
                pdb.set_trace()
            except KeyError:
                print('key error found')
                pdb.set_trace()
                
        #check if col_bins length lines up with days in month
        for month in col_bins.keys():
            bin_Length = len(col_bins[month])
            #pdb.set_trace()
            if bin_Length != days_in_month[month-1]:
                logging.warning('number of days do not match. check if data present for year: {0} and month: {1}'.format(year, month))
            
        df_month = pd.DataFrame()
        
        for month in col_bins.keys():
            month_avg = input_df[ col_bins[month] ].mean(axis = 1)
            df_month[str(year)+'_'+str(month)] = month_avg
    
        #return df 
    
        return df_month    
            
    def createTimeSeriesDf(self,directory):
        logging.debug('adding snow data to dataframe:' )  

        self.lat_long_indicies = self.df.index.tolist()
        output_df = pd.DataFrame()
        logging.debug('changing directory to: {0}'.format(directory))

        if not os.path.exists(directory):
            pdb.set_trace()
            logging.warning('directory does not exist: {0}'.format(directory))
            
        for path, dirs, files in os.walk(directory):
            logging.debug('path: {}'.format(path))
            logging.debug('dirs: {}'.format(dirs))
            for filename in [f for f in files if f.endswith(".gz")]:
                logging.debug('reading file: {}'.format(filename))
                
                with gzip.open(os.path.join(path, filename), 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    threashold = 75
                    for i, line in enumerate(lines[0:100]): 
                        if re.search('0{30,}', line):
                            logging.info('data found at index: {}'.format(i))
                            header = lines[0:i-1]
                            body = lines[i:-1]
                            int_body = body
                            for i, line in enumerate(body):
                                try:
                                    line = line.strip('\r') #sometimes there is a newline
                                    int_body[i] = [int(c) for c in line]
                                except ValueError as err:
                                    pdb.set_trace()
                                    logging.warning('value error: {0}'.format(err))
                            body_m = np.matrix(int_body)
                            
                            #need to flip matrix from left to right.
                            body_m = np.fliplr(body_m)
                            
                            
                            list(map(lambda x: body_m[x], self.lat_long_indicies))
                            colName = filename.split('_', 1)[0].replace('ims', '')
                            colName = colName[0:4]+'_'+colName[4:]
                            try:                                
                                output_df[colName] = list(map(lambda x: body_m[x], self.lat_long_indicies))
                                logging.debug('column name added: {}'.format(colName)) 
                            except:
                                pdb.set_trace()
                                logging.warning('column name not added: {}'.format(colName))
                                pass
                            
                            break
                        
                        if re.search('0    0    0    0    0    0    0    0', line):
                            logging.info('data found at index: {}'.format(i))
                            logging.debug('unpacked data found for filename: {}'.format(filename))
                            header = lines[0:i-1]
                            body = lines[i:-1]
                            int_body = []
                            for i, line in enumerate(body):
                                line = line.replace(' ','')
                                line = line.replace('164','3')
                                line = line.replace('165','4')
                                int_body.append([int(c) for c in line]) 
                            colName = filename.split('_', 1)[0].replace('ims', '')
                            colName = colName[0:4]+'_'+colName[4:]    
                            #pdb.set_trace()
                            flat_body = [item for sublist in int_body for item in sublist]
                            body_m = np.matrix([flat_body])
                            #need to flip matrix from left to right.
                            body_m = np.fliplr(body_m)
                            body_m=body_m.reshape(1024,1024)
                            reduced_body = list(map(lambda x: body_m[x], self.lat_long_indicies)) 
                            flat_body_land = self.add_land(reduced_body)   
                            
                            try:                                
                                output_df[colName] = flat_body_land
                                                                
                                logging.debug('column name added: {}'.format(colName)) 
                            except:
                                pdb.set_trace()
                                logging.warning('column name not added: {}'.format(colName))
                                pass                                                   
                            break 
                        
                                               
                        if i > threashold: #TODO: need to format the body for files with spaces in zeros
                            logging.error('cant distinguish header for filename: {}'.format(filename))
                            break              
        return output_df
                        
    #value error if this function is defined in add_land                    
    def build_terrain(self,x,y):                                    
        if y == 2:
            logging.warning( 'thats odd, water is reported on my matrix')
        if y == 3: 
            logging.warning( 'thats odd, land is being reported on my matrix')
        if self.logic_matrix[x,y] == 0:
            return x
        elif self.logic_matrix[x,y] == 1:
            return y
        else:
            logging.error( 'check logic matrix')
            return y    
                   
    def add_land(self,m):
        try:                                  
            m_with_land_list = map( lambda no_snow_elem,matrix_elem : self.build_terrain(no_snow_elem,matrix_elem), self.df['noSnowMap'].values.tolist(), m)       
            return m_with_land_list 
        except ValueError as err:
            inputLen = len(m) 
            noSnowLen = len(self.df['noSnowMap'].values.tolist())
            logging.error('lists have to be the same length: {0}'.format(err))
        
    def make_monthly_averaged_df(self,output_dir):
        df_monthly = pd.DataFrame(columns = ['remove_me'])
        os.chdir(output_dir)        
        file_names = sorted(glob.glob("*.csv"), key = lambda x: x.rsplit('.', 1)[0])
        for file in file_names:
            df = pd.read_csv(file, index_col=0)
            df_avg = self.computeMonthlyAverage(df)
            try:
                df_monthly = pd.concat([df_monthly, df_avg], axis=1)
                print('added yearly data from file: {}'.format(file))
            except ValueError as err:
                print('check number of rows in file:{}'.format(file))
                pdb.set_trace()

        df_monthly.drop('remove_me',1, inplace=True)
        pdb.set_trace()
        os.chdir(output_dir) 
        df_monthly.to_csv('monthly_averages_test.csv')

    def make_csv_files(self,zip_dir):
        output_dir = os.getcwd()+'/output/'+zip_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.chdir('data/'+zip_dir)
        for path, dirs, files in os.walk('.'):
            for folder_name in dirs:
                print('in dir:{0} '.format(folder_name))
                df_year = self.createTimeSeriesDf(folder_name)
                os.chdir('..')
                df_year.to_csv(output_dir+folder_name+'.csv')
                print('done and file saved, moving on from {0} '.format(folder_name))
        print('all done')
        