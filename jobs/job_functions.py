# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 13:01:36 2017

@author: tyler
"""

import logging
reload(logging) #need to reload in spyder
import os
import pdb

from snowCode import makeSnowHDFStore 
from generate_grid_and_area import grid_and_area
from plot_snow_on_map import plotSnow 
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


def plot_points_on_basemap(filename,df, lat_long_coords, show = True, save = True,width = 4500000,height = 4000000):

    #make map
    fig = plt.figure(0)
    long_center, lat_center = ((lat_long_coords['upper_long']-lat_long_coords['lower_long'])/2+lat_long_coords['lower_long'],(lat_long_coords['upper_lat']-lat_long_coords['lower_lat'])/2+lat_long_coords['lower_lat'])
    
    m = Basemap(projection='laea',
                width = width,
                height = height,
                resolution='c',lat_0=lat_center,lon_0=long_center)
    
    x, y = m(df['long'].values.tolist(), df['lat'].values.tolist()) # this function converts degrees to meters on this reference map

    m.scatter(x, y, marker='.',color='cyan', alpha=.1)

    m.bluemarble()
    

    if show:
        plt.show()
    if save:
        plot_dir = os.path.join(os.getcwd(),'plots')
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        plt.savefig(os.path.join(plot_dir,filename+'.png'))
        if not show:
            plt.close()

def run_job(input_dict, make_grid = True, make_hdf5 = True, make_time_series_df = True, make_plots = True):
    
    if not os.path.exists('logs'):  
        os.mkdir('logs')
            
    filename = input_dict['filename']
    logging.basicConfig(filename=os.path.join('logs',filename+'.log'),level=logging.DEBUG)
    logging.debug('Start of log file')  
    
    home_dir = os.getcwd()
    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))
    
    ftp_filename = input_dict['ftp_filename']
    grid_size = input_dict['grid_size']
    no_snow_planet_name = input_dict['no_snow_planet_name']
    lat_grid_filename = input_dict['lat_grid_filename']
    lon_grid_filename = input_dict['lon_grid_filename']
    lat_long_area_filename = input_dict['lat_long_area_filename']
    lat_long_coords = input_dict['lat_long_coords']
    
    
    #initialize object   
    if make_grid:
        logging.info('making grids for: {}'.format(filename))
        grid_maker = grid_and_area(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
        
        
        grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
        grid_maker.reduceLatLong()
        grid_maker.makeNoSnowMap()
        
        grid_maker.addAreas()
        
        grid_maker.df.to_csv(os.path.join(data_dir,lat_long_area_filename ))
        
        if filename == 'Artic-24km':
            plot_points_on_basemap(filename,grid_maker.df, lat_long_coords, show = False, save = True,width = 8500000,height = 10000000)
        else:
            plot_points_on_basemap(filename,grid_maker.df, lat_long_coords, show = False, save = True)
    
    
    
    if make_hdf5:
        input_zip_dir = os.path.join(home_dir,os.pardir,os.pardir,'zip_files',ftp_filename)
        output_dir = os.path.join(input_zip_dir,os.pardir,os.pardir,'output',filename)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        
        #first make hdf5 database using unitTest directory
        makeHDF = makeSnowHDFStore(data_dir,
                                   output_dir,
                                   input_zip_dir,
                                   lat_long_area_filename,
                                   lat_long_coords)
        logging.info('Start parsing through compressed files')
        makeHDF.make_hdf5_files()
    
        if make_time_series_df:
            df = makeHDF.make_coverage_df()
            df.to_csv(os.path.join(output_dir, filename+'.csv'))
        
    if make_plots:
        plotHDF = plotSnow(data_dir,lat_long_area_filename,lat_long_coords)
        plotHDF.set_up_grid()
        plotHDF.make_plots_from_HDFStore(output_dir, show = False, save = True)