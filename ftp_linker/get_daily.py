# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 11:08:04 2017

@author: tyler
"""

from ftplib import FTP
import datetime
import urlparse
import logging
import os
import gzip
reload(logging) #need to reload in spyder
from snowCode import makeSnowHDFStore 
from plot_snow_on_map import plotSnow
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata
import numpy as np

import pdb

class plotSnowCSV(plotSnow):
    
    """
    Plot a single csv file
    """
    def __init__(self,data_dir,lat_long_area_filename, lat_long_coords):
        plotSnow.__init__(self,data_dir,lat_long_area_filename, lat_long_coords)
    
    
    def make_plot_from_CSV(self, series_name, show = True, save = False):
        plt.ioff()
        
        my_series = pd.Series.from_csv(series_name)
        
        timestamp = series_name.strip('/series_')
        m=self.makeMap('merc')
        data = my_series.apply(self.snow_and_ice)
        grid_z0 = griddata(self.points, data.values, (self.grid_x, self.grid_y), method='linear') #can be nearest, linear, or cubic interpolation
        grid_z0[ grid_z0 != 1 ] = np.nan
        m.contourf(self.grid_x, self.grid_y,grid_z0, latlon=False, cmap = self.cmap1, alpha=1)
        plt.title(timestamp,fontsize=16, color = "black")
        if show:
            plt.show()
        if save:
            plt.savefig(timestamp+'.png')
            plt.close()   

class makeSnowCSV(makeSnowHDFStore):
    """
    create a single time series object and save it as a csv.
    """

    def __init__(self,data_dir, lat_long_area_filename,lat_long_coords):
        makeSnowHDFStore.__init__(self,data_dir,lat_long_area_filename,lat_long_coords)

    def createTimeSeriesCSV(self,filename):
        logging.debug('inside createTimeSeriesCSV:' )  

        logging.debug('reading file: {}'.format(filename))
        
        colName = filename.split('_', 1)[0].replace('ims', '')
        colName = colName[0:4]+'_'+colName[4:]
        dt = datetime.datetime.strptime(colName,'%Y_%j')
        series_name = dt.strftime('series_%Y_%m_%d')

        with gzip.open(filename, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            nominally_formatted_bool, body = self.check_if_nominally_formatted(lines, filename)
            
            if nominally_formatted_bool:
                try:
                    data = self.parse_normally_formatted_file(body, filename)
                    s = pd.Series(data)
                    s.to_csv(series_name)
                    logging.debug('created series for normally formatted filename: {}'.format(filename))
                except:
                    
                    logging.warning('cant distinguish data for normally formatted filename: {}. Not added'.format(filename))
                    pass
            elif not nominally_formatted_bool:
                try:
                    data = self.parse_alternatively_formatted_file(body,filename)
                    s = pd.Series(data)
                    s.to_csv(series_name)
                    logging.debug('created series for  alternatively formatted filename: {}'.format(filename))
                except:
                    
                    logging.warning('cant distinguish data for alternatively formatted filename: {}. Not added'.format(filename))
                    pass

            if not 4 in body:
                logging.warning('no snow reported for filename: {}'.format(filename))
        return series_name
                        

def get_daily_folder(resolution_folder):

    today = datetime.datetime.now()
    url = urlparse.urlparse('ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
    IMS_path = 'DATASETS/NOAA/G02156/'
    
    year_folder = today.strftime('%Y')
    
    prefix = 'ims'
    postfix = '_24km_v1.3.asc.gz'
    day_filename = today.strftime(prefix+'%Y%j'+postfix)
    
    ftp = FTP(url.netloc)    # connect to host, default port
    ftp.login()                     # user anonymous, passwd anonymous@
    ftp.cwd(IMS_path)               # change into "debian" directory
    #ftp.retrlines('LIST')           # list directory contents
    ftp.cwd(resolution_folder)
    ftp.cwd(year_folder)
    
    try:
        with open(day_filename, 'w') as fobj:
            ftp.retrbinary("RETR " + day_filename ,fobj.write)
    except:
        print "Error"
    
    ftp.quit()
    return day_filename


if __name__ == '__main__': 
    logging.basicConfig(filename='get_daily.log',level=logging.INFO)
    logging.info('Time of log file: {0}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    twenty_four_dir = '24km'
    four_dir = '24km'
    home_dir = os.getcwd()
    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))
    input_zip_dir = home_dir
    lat_long_area_filename = 'lat_long_centroids_area_24km.csv'
    lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long

    logging.info('Retrieving today\'s data')
    
    twenty_four_day_filename = get_daily_folder(twenty_four_dir)
    

    logging.info('Creating today\'s csv')
    makeCSV = makeSnowCSV(data_dir,lat_long_area_filename,lat_long_coords)  
    series_name = makeCSV.createTimeSeriesCSV(twenty_four_day_filename)
    
    logging.info('Start of plotting section')
    plotHDF = plotSnowCSV(data_dir,lat_long_area_filename,lat_long_coords)
    plotHDF.make_plot_from_CSV(series_name, show = False, save = True)