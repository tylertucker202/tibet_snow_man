# -*- coding: utf-8 -*-
import logging
reload(logging) #need to reload in spyder
import os
from snowCode import makeSnowDF 
import pdb

if __name__ == '__main__': 
    logging.basicConfig(filename='snowCode.log',level=logging.WARNING)
    logging.debug('Start of log file')

    home_dir = os.getcwd()
    data_dir = home_dir+'/data/'
    input_zip_dir = '24km_test/'
    lat_long_area_filename = 'lat_long_centroids_area_24km.csv'
    lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    
    #initialize object
    makeDF = makeSnowDF(data_dir,lat_long_area_filename,lat_long_coords)
    
    
    logging.info('Start parsing through compressed files')
    
    logging.info('Start parsing through compressed files')        
    #makeDF.make_csv_files(input_zip_dir)
    
    logging.info('Start of making monthly averaged dataframe')
    #use to loop through completed files
    #makeDF.make_monthly_averaged_df(home_dir+'/output/'+input_zip_dir)
    