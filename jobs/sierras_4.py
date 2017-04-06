# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:03:55 2017

@author: tyler
"""

# -*- coding: utf-8 -*-
import logging
reload(logging) #need to reload in spyder
import os
import pdb
import datetime
from snowCode import makeSnowHDFStore 
from generate_grid_and_area import grid_and_area
from region_parameters import get_sierras_4x4_param, plot_basemap
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


def plot_basemap(filename, lat_long_coords, show = True, save = True):
    
    #make map
    fig = plt.figure(2)
    long_center, lat_center = ((lat_long_coords['upper_long']-lat_long_coords['lower_long'])/2+lat_long_coords['lower_long'],(lat_long_coords['upper_lat']-lat_long_coords['lower_lat'])/2+lat_long_coords['lower_lat'])
    
    m = Basemap(projection='laea',
                width = 4500000,
                height = 4000000,
                resolution='c',lat_0=lat_center,lon_0=long_center)
    x, y = m(long_center, lat_center) # this function converts degrees to meters on this reference map
    top_left = m(lat_long_coords['lower_long'],lat_long_coords['upper_lat'])
    top_right = m(lat_long_coords['upper_long'],lat_long_coords['upper_lat'])
    bottom_left = m(lat_long_coords['lower_long'],lat_long_coords['lower_lat'])
    bottom_right = m(lat_long_coords['upper_long'],lat_long_coords['lower_lat'])
    print('center point x: {} meters'.format(x))
    print('center point y: {} meters'.format(y))
    m.plot(x, y, marker='D',color='cyan')
    m.plot(top_left[0],top_left[1], marker='D',color='cyan')
    m.plot(top_right[0], top_right[1], marker='D',color='cyan')
    m.plot(bottom_left[0], bottom_left[1], marker='D',color='cyan')
    m.plot(bottom_right[0], bottom_right[1], marker='D',color='cyan')
    m.bluemarble()
    if show:
        plt.show()
    if save:
        plot_dir = os.path.join(os.getcwd(),'plots')
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        plt.savefig(os.path.join(plot_dir,filename+'.png'))
        plt.close()
    return fig


if __name__ == '__main__':
    logging.basicConfig(filename='sierras_4.log',level=logging.INFO)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()

    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))

    filename, grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename, lat_long_coords = get_sierras_4x4_param()

    
    #initialize object
    
    grid_maker = grid_and_area(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
    
    logging.info('make lat long, and area dataframe')
    
    grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
    grid_maker.reduceLatLong()

    #add areas. this takes awhile.
    grid_maker.addAreas()
    grid_maker.df.to_csv(lat_long_area_filename)
    plot_basemap(filename, lat_long_coords, show = False, save = True)
