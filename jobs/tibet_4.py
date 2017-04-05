# -*- coding: utf-8 -*-
import logging
reload(logging) #need to reload in spyder
import os
import pdb
import datetime
from snowCode import makeSnowHDFStore 
from generate_grid_and_area import grid_and_area, get_24x24_param, get_4x4_param

if __name__ == '__main__':
    logging.basicConfig(filename='tibet_4.log',level=logging.WARNING)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()

    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))

    #grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename = get_24x24_param()
    grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename = get_4x4_param()

    tibet_lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    
    #initialize object
    
    grid_maker = grid_and_area(tibet_lat_long_coords,data_dir,no_snow_planet_name,grid_size)
    
    logging.info('make lat long, and area dataframe')
    
    grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
    grid_maker.reduceLatLong()
    grid_maker.makeNoSnowMap()
        
    #tibet falls approximatly in this region.
    grid_maker.addAreas()
    
    grid_maker.df.to_csv(os.path.join(home_dir,lat_long_area_filename) )
