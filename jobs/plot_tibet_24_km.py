# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 13:43:05 2017

@author: tyler
"""
import logging
import os
import sys
sys.path.append(os.pardir)
from plotSnow import plotSnow
from region_parameters import get_test_tibet_24x24_param

if __name__ == '__main__':
    reload(logging)  # spyder sometimes needs logging to reload.
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='plotSnow.log',
                        level=logging.DEBUG)
    logging.debug('\nStart of log file')
    home_dir = os.getcwd()
    GRID_SIZE = 1024
    OUTPUT_DICT = get_test_tibet_24x24_param()

    OUTPUT_DIR = os.path.join(home_dir,
                              os.pardir,
                              os.pardir,
                              'output',
                              OUTPUT_DICT['filename'])
    LAT_LON_COORDS = OUTPUT_DICT['lat_lon_coords']
    YEARS = map(lambda x: str(x), range(1997, 2006))

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # init database
    DB_NAME = 'twenty_four'
    AREAS_COLLECTION_NAME = 'twenty_four_km_areas'
    TIME_SERIES_COLLECTION_NAME = 'combined_dates'
    RESOLUTION = '24km'

    plotter = plotSnow(DB_NAME,
                       RESOLUTION,
                       GRID_SIZE,
                       AREAS_COLLECTION_NAME,
                       TIME_SERIES_COLLECTION_NAME,
                       LAT_LON_COORDS,
                       OUTPUT_DIR)
    #plotter.add_timeseries_from_ftp(YEARS, SHOW=False, SAVE=False)
    plotter.make_plots_from_collections(YEARS, SHOW=False, SAVE=False)
