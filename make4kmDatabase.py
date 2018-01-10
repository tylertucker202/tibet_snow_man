#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 12:50:20 2018

@author: tyler
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 12:13:07 2018

@author: tyler
"""
from gridAndArea import gridAndArea
from makeMongoDatabase import makeMongoDatabase
import os
from region_parameters import get_4x4_param
import logging


if __name__ == '__main__':
    # create a logging format
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='make4kmDatabase.log', level=logging.DEBUG)
    logging.debug('\nStart of log file')
    home_dir = os.getcwd()

    DATA_DIR = os.path.join(home_dir, 'data')
    DB_NAME = 'IMSFOUR'
    output_dict = get_4x4_param()

    GRID_SIZE = output_dict['grid_size']
    no_snow_planet_name = output_dict['no_snow_planet_name']
    LAT_GRID_FILENAME = output_dict['lat_grid_filename']
    LON_GRID_FILENAME = output_dict['lon_grid_filename']
    lat_long_area_filename = output_dict['lat_lon_area_filename']
    
    """
    Create HDF5 areas
    """

    # initialize class
    ga = gridAndArea(lat_long_area_filename, DATA_DIR, GRID_SIZE)

    # initialize h5. WARNING: THIS WILL ERASE THE EXISTING .H5
    ga.init_h5(LAT_GRID_FILENAME, LON_GRID_FILENAME)

    # make centroids
    """
    Large jobs are sometimes halted.
    START_ROW lets you continue where you left off."""
    START_ROW = 1
    ga.make_centroids(START_ROW)

    # make cartesian centroid coordinates
    ga.create_centroid_cartesian()

    # make areas
    ga.make_areas()

    ga.make_no_snow_map(no_snow_planet_name, save=True)
    
    """
    Add hdf5 file to database
    """
    
    AREAS_COLLECTION_NAME = 'areas'
    HDF5_FILE = os.path.join(DATA_DIR, lat_long_area_filename)
    mdb = makeMongoDatabase(GRID_SIZE, DB_NAME, AREAS_COLLECTION_NAME)
    mdb.add_area_collection(HDF5_FILE)