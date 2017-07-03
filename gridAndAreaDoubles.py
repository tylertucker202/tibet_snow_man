# -*- coding: utf-8 -*-
'''
Created on Sun Apr 30 09:45:57 2017

@author: tyler
'''

import os
import sys
import re
import h5py
import logging

import numpy as np
import pdb
import matplotlib.pylab as plt
sys.path.append(os.pardir)
reload(logging)
from region_parameters import get_24x24_param
from mpl_toolkits.basemap import Basemap
from gridAndArea import gridAndArea


class gridAndAreaDoubles(gridAndArea):
    """
    Used for large 1x1km resolution files, which use doubles."""
    def __init__(self,
                 HDF5_NAME,
                 DATA_DIR,
                 LAT_GRID_FILENAME,
                 LON_GRID_FILENAME,
                 GRID_SIZE
                 ):
        gridAndArea.__init__(self,
                             HDF5_NAME,
                             DATA_DIR,
                             LAT_GRID_FILENAME,
                             LON_GRID_FILENAME,
                             GRID_SIZE
                             )

    def __exit__(self):
        self.fh5.close()

    def init_h5(self, LAT_GRID_FILENAME, LON_GRID_FILENAME):
        logging.debug('initializing h5')

        fh5 = h5py.File(self.HDF5_NAME, 'w')

        logging.debug('getting Latitude and Longitude arrays:')

        logging.debug('getting Latitude and Longitude arrays:')

        try:
            with open(os.path.join(self.DATA_DIR,
                                   LAT_GRID_FILENAME), 'r') as f:
                lat_array = np.fromfile(f, dtype=np.double64)

                # matrix version
                lat_m = lat_array.reshape(self.GRID_SIZE, self.GRID_SIZE)
                # list starts at bottomf left corner. need to rearrange
                lat_mud = np.flipud(lat_m)
                fh5.create_dataset('lat',
                                   (self.GRID_SIZE, self.GRID_SIZE),
                                   data=lat_mud,
                                   fillvalue=np.nan,
                                   compression='lzf')
                fh5.flush()
                logging.debug('lat matrix loaded')

                logging.debug('lat array loaded')

            with open(os.path.join(self.DATA_DIR,
                                   LON_GRID_FILENAME), 'r') as f:
                lon_array = np.fromfile(f, dtype=np.float32)
                lon_m = lon_array.reshape(self.GRID_SIZE, self.GRID_SIZE)
                lon_mud = np.flipud(lon_m)
                fh5.create_dataset('lon',
                                   (self.GRID_SIZE, self.GRID_SIZE),
                                   data=lon_mud,
                                   fillvalue=np.nan,
                                   compression='lzf')
                fh5.flush()
                logging.debug('lon matrix loaded')

        except:
            logging.debug('somthing went wrong when loading arrays')
            os.path.exists(self.DATA_DIR)
            os.listdir(self.DATA_DIR)
            os.path.isfile(os.path.join(self.DATA_DIR, LAT_GRID_FILENAME))
            os.path.isfile(os.path.join(self.DATA_DIR, LON_GRID_FILENAME))
            logging.error('files were not loaded...check path?')
        fh5.close()
        logging.debug('exiting function: init_h5')

if __name__ == '__main__':
    # create a logging format
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='gridAndAreaDoubles.log', level=logging.DEBUG)
    logging.debug('Start of log file')
    home_dir = os.getcwd()

    DATA_DIR = os.path.join(home_dir, os.pardir, 'data')
    output_dict = get_24x24_param()

    GRID_SIZE = output_dict['grid_size']
    no_snow_planet_name = output_dict['no_snow_planet_name']
    LAT_GRID_FILENAME = output_dict['lat_grid_filename']
    LON_GRID_FILENAME = output_dict['lon_grid_filename']
    lat_long_area_filename = output_dict['lat_lon_area_filename']

    # initialize h5
    ga = gridAndArea(lat_long_area_filename,
                     DATA_DIR,
                     LAT_GRID_FILENAME,
                     LON_GRID_FILENAME,
                     GRID_SIZE)

    # make centroids
    ga.make_centroids()

    # make cartesian centroid coordinates
    ga.create_centroid_cartesian()

    # make areas
    ga.make_areas()

    ga.make_no_snow_map(no_snow_planet_name, save=False)
