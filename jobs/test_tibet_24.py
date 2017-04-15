# -*- coding: utf-8 -*-
import logging
reload(logging) #need to reload in spyder
import os
import pdb

from snowCode import makeSnowHDFStore 
from generate_grid_and_area import grid_and_area
from plot_snow_on_map import plotSnow 
from region_parameters import get_test_tibet_24x24_param, plot_points_on_basemap


if __name__ == '__main__':
    
    logging.basicConfig(filename=os.path.join('logs','test_tibet_24.log'),level=logging.DEBUG)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()

    
    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))
    
    
    input_dict = get_test_tibet_24x24_param()
    
    ftp_filename = input_dict['ftp_filename']
    filename = input_dict['filename']
    grid_size = input_dict['grid_size']
    no_snow_planet_name = input_dict['no_snow_planet_name']
    lat_grid_filename = input_dict['lat_grid_filename']
    lon_grid_filename = input_dict['lon_grid_filename']
    lat_long_area_filename = input_dict['lat_long_area_filename']
    lat_long_coords = input_dict['lat_long_coords']
    
    
    #initialize object   
#    grid_maker = grid_and_area(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
#    
#    logging.info('make lat long, and area dataframe')
#    
#    grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
#    grid_maker.reduceLatLong()
#    grid_maker.makeNoSnowMap()
#
#    grid_maker.addAreas()
#    
#    grid_maker.df.to_csv(os.path.join(data_dir,lat_long_area_filename ))
#    
#    plot_points_on_basemap(filename,grid_maker.df, lat_long_coords, show = False, save = True)




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
    #makeHDF.make_hdf5_files()
    
    df = makeHDF.make_coverage_df()
    df.to_csv(os.path.join(output_dir,filename+'.csv'))
    
    logging.info('Start plotting from database')
    plotHDF = plotSnow(data_dir,lat_long_area_filename,lat_long_coords)
    plotHDF.set_up_grid()
    plotHDF.make_plots_from_HDFStore(output_dir, show = False, save = True)
   