# -*- coding: utf-8 -*-
import logging
reload(logging) #need to reload in spyder
import os
import pdb
import datetime
from plot_snow_on_map import plotSnow
from snowCode import makeSnowHDFStore 

if __name__ == '__main__': 
    logging.basicConfig(filename='snowCode.log',level=logging.DEBUG)
    logging.debug('Time of log file: {0}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    home_dir = os.getcwd()
    data_dir = home_dir+'/data/'
    input_zip_dir = 'zip_files/4km_1/'
    lat_long_area_filename = 'lat_long_centroids_area_4km.csv'
    lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    
    #initialize object
    makeHDF = makeSnowHDFStore(data_dir,lat_long_area_filename,lat_long_coords)    
    logging.info('Start parsing through compressed files section')
    makeHDF.make_hdf5_files(input_zip_dir)
    logging.info('Start making coverage timeseries section')
    df_cov = makeHDF.make_coverage_df('output/'+input_zip_dir)
    df_cov['perc coverage'].plot()
#    df_cov.to_csv('output/'+input_zip_dir+'/24_km.csv')
    
    #identify any anomolies
    all_snow = df_cov[  (df_cov['perc coverage'] == 1) ].index.tolist()
    suspect_dates = map(lambda x: x.strftime('%Y-%j'), all_snow)
    no_snow = df_cov[  (df_cov['perc coverage'] == 0) ].index.tolist()
    suspect_dates.append(map(lambda x: x.strftime('%Y-%j'), no_snow))
#    #Plotting section
    logging.info('Start of plotting section')
    #plotHDF = plotSnow(lat_long_area_filename,lat_long_coords)
    #plotHDF.make_plots_from_HDFStore('output/'+input_zip_dir, show = False, save = True)