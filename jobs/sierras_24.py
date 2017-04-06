# -*- coding: utf-8 -*-
import logging
reload(logging) #need to reload in spyder
import os
import pdb
import datetime
from snowCode import makeSnowHDFStore 
from generate_grid_and_area import grid_and_area
from region_parameters import get_sierras_24x24_param, plot_basemap
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


if __name__ == '__main__':
    logging.basicConfig(filename='sierras_24.log',level=logging.INFO)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()

    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))

    filename, grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename, lat_long_coords = get_sierras_24x24_param()

    
    #initialize object
    
    grid_maker = grid_and_area(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
    
    logging.info('make lat long, and area dataframe')
    
    grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
    grid_maker.reduceLatLong()

    #tibet falls approximatly in this region.
    grid_maker.addAreas()
    grid_maker.df.to_csv(lat_long_area_filename)
    plot_basemap(filename, lat_long_coords, show = False, save = True)