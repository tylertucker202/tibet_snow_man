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
from region_parameters import get_24x24_param
from mpl_toolkits.basemap import Basemap


class gridAndArea:
    def __init__(self,
                 HDF5_NAME,
                 DATA_DIR,
                 GRID_SIZE
                 ):
        self.HDF5_NAME = os.path.join(DATA_DIR, HDF5_NAME)
        self.DATA_DIR = DATA_DIR
        self.GRID_SIZE = GRID_SIZE
        logging.debug('exiting function: __init__')

    def __exit__(self):
        self.fh5.close()

    def init_h5(self, LAT_GRID_FILENAME, LON_GRID_FILENAME):
        logging.debug('initializing h5')
        fh5 = h5py.File(self.HDF5_NAME, 'w')  # has to be 'w'
        logging.debug('getting Latitude and Longitude arrays:')
        try:
            with open(os.path.join(self.DATA_DIR,
                                   LAT_GRID_FILENAME), 'r') as f:
                """
                note: projection points outside earth are included
                example: the first lat is at -20, even though there are no
                land and sea values reported."""
                lat_array = np.fromfile(f, dtype=np.float32)

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

        logging.debug('making datasets')
        fh5.create_dataset('lat_centroid',
                           (self.GRID_SIZE,
                            self.GRID_SIZE),
                           dtype='float32',
                           fillvalue=np.nan,
                           compression='lzf')
        fh5.create_dataset('lon_centroid',
                           (self.GRID_SIZE,
                            self.GRID_SIZE),
                           dtype='float32',
                           fillvalue=np.nan,
                           compression='lzf')
        fh5.create_dataset('areas',
                           (self.GRID_SIZE, self.GRID_SIZE),
                           dtype='float64',
                           compression='lzf')
        fh5.create_dataset('y_centroid',
                           (self.GRID_SIZE, self.GRID_SIZE),
                           dtype='float64',
                           fillvalue=np.nan,
                           compression='lzf')
        fh5.create_dataset('x_centroid',
                           (self.GRID_SIZE, self.GRID_SIZE),
                           dtype='float64',
                           fillvalue=np.nan,
                           compression='lzf')
        fh5.create_dataset('land_sea_values',
                           (self.GRID_SIZE, self.GRID_SIZE),
                           dtype='i8',
                           fillvalue=np.nan,
                           compression='lzf')
        fh5.close()
        logging.debug('exiting function: init_h5')

    def make_centroids(self, START_ROW=1):
        '''making centroids starting with:
        the 2nd row, 2nd column,
        ending at the 2nd to last row,
        2nd to last column.
        '''
        logging.debug('making centroids')
        fh5 = h5py.File(self.HDF5_NAME, 'r+')
        lat_dset = fh5.get('lat')
        lon_dset = fh5.get('lon')
        lat_centroid_dset = fh5.get('lat_centroid')
        lon_centroid_dset = fh5.get('lon_centroid')

        for row in range(START_ROW, self.GRID_SIZE-1):
            lat_seg = lat_dset[row: row+2, :]
            lon_seg = lon_dset[row: row+2, :]
            lat_mean = []
            lon_mean = []
            for col in range(1, self.GRID_SIZE-1):
                try:
                    lat_points = lat_seg[0:2, col:col+2]  # gets 4 points
                    lat_mean.append(lat_points.mean())
                    lon_points = lon_seg[0:2, col:col+2]  # gets 4 points
                    lon_mean.append(lon_points.mean())
                except ValueError:
                    pdb.set_trace()
                    logging.error('somthing went wrong when making centroids')
            try:
                lat_centroid_dset[row, 1: self.GRID_SIZE-1] = lat_mean
                lon_centroid_dset[row, 1: self.GRID_SIZE-1] = lon_mean
            except IOError:
                pdb.set_trace()
                logging.error('somthing went wrong when making centroids')
            if row % 250 == 0:
                # pdb.set_trace()
                logging.debug('on row: {0} col: {1}'.format(row, col))
                logging.debug('flushing hdf5')
                fh5.flush()

        fh5.flush()
        fh5.close()
        logging.debug('exiting function: make_centroids')

    def create_centroid_cartesian(self):
        '''converts centroids from lat,lon
        to a Lambert azumithal equal area projection
        '''
        logging.debug('converting centroids to cartesian coordinates')

        fh5 = h5py.File(self.HDF5_NAME, 'r+')
        lat_centroid_dset = fh5.get('lat_centroid')
        lon_centroid_dset = fh5.get('lon_centroid')
        y_centroid_dset = fh5.get('y_centroid')
        x_centroid_dset = fh5.get('x_centroid')

        """basemap is used to convert points from lat, long
        to m in x and y. laea projection conserves area
        """
        center = (90.0, 0.0)
        m = Basemap(projection='laea',
                    width=4500000,
                    height=4000000,
                    resolution='c', lat_0=center[0], lon_0=center[1])

        for idx in range(1, lat_centroid_dset.shape[0]):
            if idx % 250 == 0:
                logging.debug('on row: {0} '.format(idx))
                logging.debug('flushing hdf5')
                fh5.flush()
            lat_row = lat_centroid_dset[idx, :]
            lon_row = lon_centroid_dset[idx, :]
            x, y = m(lon_row, lat_row)
            x[x == 1e+30] = np.nan  # replace with nan
            y[y == 1e+30] = np.nan  # replace with nan
            x_centroid_dset[idx, :], y_centroid_dset[idx, :] = x, y  # meters
        fh5.flush()
        fh5.close()
        logging.debug('exiting function: create_centroid_cartesian')

    def make_areas(self):
        '''making areas for each grid cell, starting with:
        the 2nd row, 2nd column,
        ending with:
        the 2nd to last row,
        2nd to last column.
        '''
        logging.debug('making area')
        fh5 = h5py.File(self.HDF5_NAME, 'r+')
        yy = fh5.get('y_centroid')
        xx = fh5.get('x_centroid')
        areas_dset = fh5.get('areas')
        for row in range(1, (self.GRID_SIZE-1)):
            row_areas = []
            # get a 2xn segment for the whole row
            xx_seg = xx[row-1:row+1, :]
            yy_seg = yy[row-1:row+1, :]
            for col in range(1, (self.GRID_SIZE-1)):
                try:
                    inp_x = [xx_seg[1, col-1],
                             xx_seg[1, col],
                             xx_seg[0, col],
                             xx_seg[0, col-1]]
                    inp_y = [yy_seg[1, col-1],
                             yy_seg[1, col],
                             yy_seg[0, col],
                             yy_seg[0, col-1]]
                    if not (np.isnan(inp_x).any() or np.isnan(inp_y).any()):
                        row_areas.append(self.polygon_area(inp_x, inp_y))
                    else:
                        row_areas.append(np.nan)
                except:
                    pdb.set_trace()
                    logging.error('somthing went wrong when making areas')
            try:
                areas_dset[row, 1:self.GRID_SIZE-1] = row_areas
            except:
                pdb.set_trace()
                logging.error('somthing went wrong when adding row {}'
                              'to areas'.format(row))
            if row % 250 == 0:
                # pdb.set_trace()
                logging.debug('on row: {0} col: {1}'.format(row, col))
                logging.debug('flushing hdf5')
                fh5.flush()

        fh5.flush()
        fh5.close()
        logging.debug('exiting function: make_areas')

    @staticmethod
    def polygon_area(x, y):
        '''shoestring formula is applied
        for points centered around row,col.
        function converts from m^2 into km^2.
        '''
        area = 0.5 * np.abs(
            np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) / (10 ** 6)
        return area

    def make_no_snow_map(self, no_snow_map_name, save=False):
        '''Make a .png that shows what your map looks like without snow or
        ice. Used to check if projection looks OK, but is currently not unit
        tested.

        Also adds land_sea_values field to hdf5
        '''
        filename = no_snow_map_name
        logging.debug("""getting map with no snow and ice, \
                      used for uncompressed plots, as they \
                      don\'t distinguish between land and sea""")
        logging.debug('reading file: {}'.format(filename))
        fh5 = h5py.File(self.HDF5_NAME, 'r+')
        land_sea_values = fh5.get('land_sea_values')
        with open(os.path.join(self.DATA_DIR, filename), 'r') as f:
            content = f.read()
            lines = content.split('\n')

            threashold = 75
            for i, line in enumerate(lines[0:100]):
                if re.search('0{30,}', line):
                    logging.info('data found at index: {}'.format(i))
                    body = lines[i:-1]
                    break
                if i > threashold:
                    logging.error("""cant distinguish header \
                                  for filename: {}""".format(filename))
                    break
            int_body = body  # prevents altering the recursion
            for i, line in enumerate(body):
                # ice and and snow is changed to sea and land respectively
                line = line.replace('3', '1')
                line = line.replace('4', '2')
                int_line = [int(c) for c in line]
                land_sea_values[i, :] = int_line

                int_body[i] = int_line

        def rbg_convert(x):
            snow = (5, 5, 5)
            terra = (0, 128, 0)
            sea = (0, 0, 139)
            ice = (24, 25, 26)
            firmament = (0, 0, 0)

            if x == 0:
                return firmament
            elif x == 1:
                return sea
            elif x == 2:
                return terra
            elif x == 3:
                return ice
            elif x == 4:
                return snow
            else:
                print('no earth feature identified for point: {}'.format(x))
                return(x, 0, 0)

        if save:
            no_snow_matrix = np.matrix(int_body)
            rbg_no_snow_matrix = list(map(rbg_convert, no_snow_matrix.flat))
            RBG_ARRAY = np.array(rbg_no_snow_matrix, dtype='uint8')
            self.rbg_no_snow_matrix = RBG_ARRAY.reshape((self.GRID_SIZE,
                                                         self.GRID_SIZE, 3))
            plt.ioff()
            plt.figure()
            plt.imshow(self.rbg_no_snow_matrix)
            filename = filename.strip('.asc')
            figure_name = os.path.join(self.DATA_DIR, filename+'.png')
            plt.savefig(figure_name)
        plt.close()

if __name__ == '__main__':
    # create a logging format
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='gridAndArea.log', level=logging.DEBUG)
    logging.debug('\nStart of log file')
    home_dir = os.getcwd()

    DATA_DIR = os.path.join(home_dir, 'data')
    output_dict = get_24x24_param()

    GRID_SIZE = output_dict['grid_size']
    no_snow_planet_name = output_dict['no_snow_planet_name']
    LAT_GRID_FILENAME = output_dict['lat_grid_filename']
    LON_GRID_FILENAME = output_dict['lon_grid_filename']
    lat_long_area_filename = output_dict['lat_lon_area_filename']

    # initialize class
    ga = gridAndArea(lat_long_area_filename,
                     DATA_DIR,
                     GRID_SIZE)

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
