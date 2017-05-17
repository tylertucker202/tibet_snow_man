# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 09:45:57 2017

@author: tyler
"""

import h5py
import logging
reload(logging)
import os
import sys
sys.path.append(os.pardir)
from region_parameters import get_4x4_param
import numpy as np
import pdb
from mpl_toolkits.basemap import Basemap
import matplotlib.pylab as plt
import re
#import matplotlib.pyplot as plt

class grid_and_area:
    
    def __init__(self,
             hdf5_name,
             data_dir,
             lat_grid_filename,
             lon_grid_filename,
             grid_size
             ):
                 
        self.hdf5_name = os.path.join(data_dir,hdf5_name)
        self.data_dir = data_dir
        self.grid_size = grid_size
        
        self.init_h5(lat_grid_filename,lon_grid_filename)
        logging.debug('exiting function: __init__')
        
    def __exit__(self):
        self.fh5.close()
        
    def init_h5(self,lat_grid_filename,lon_grid_filename):
        logging.debug('initializing h5' )
    
        fh5 = h5py.File(self.hdf5_name, "w")
        
        logging.debug('getting Latitude and Longitude arrays:' )
        
        logging.debug('getting Latitude and Longitude arrays:' )
                                     
        try: 
            with open(os.path.join(self.data_dir,lat_grid_filename), "r") as f:
                lat_array = np.fromfile(f, dtype=np.float32)              
                #list starts at bottomf left corner. need to rearrange
                
                #matrix version
                lat_m = lat_array.reshape(self.grid_size,self.grid_size)
                lat_mud = np.flipud(lat_m)               
                lat_dset = fh5.create_dataset('lat', (self.grid_size, self.grid_size), data=lat_mud,fillvalue=np.nan, compression="lzf")
                fh5.flush()
                logging.debug('lat matrix loaded')
    
                logging.debug('lat array loaded')
    
            with open(os.path.join(self.data_dir,lon_grid_filename), "r") as f:
                lon_array = np.fromfile(f, dtype=np.float32)   
                lon_m = lon_array.reshape(self.grid_size,self.grid_size)
                lon_mud = np.flipud(lon_m)               
                lon_dset = fh5.create_dataset('lon', (self.grid_size, self.grid_size), data=lon_mud,fillvalue=np.nan, compression="lzf")
                fh5.flush()
                logging.debug('lon matrix loaded')            
    
        except:
            logging.debug('somthing went wrong when loading arrays')
            os.path.exists(self.data_dir)
            os.listdir(self.data_dir)
            os.path.isfile(os.path.join(self.data_dir,lat_grid_filename))
            os.path.isfile(os.path.join(self.data_dir,lon_grid_filename))
            logging.error('files were not loaded...check path?')
            pdb.set_trace()
        fh5.close()
        logging.debug('exiting function: init_h5')
    
    def make_centroids(self):
        """
        making centroids starting with:
        the 2nd row, 2nd column, 
        ending at the 2nd to last row, 
        2nd to last column.
        """

        logging.debug('making centroids')
        fh5 = h5py.File(self.hdf5_name, "r+")
        lat_dset = fh5.get('lat')
        lon_dset = fh5.get('lon')
        

        index_array  = np.mgrid[1:self.grid_size-1,
                                1:self.grid_size-1].swapaxes(0,2).swapaxes(0,1)
        centroids_index = index_array.reshape((self.grid_size-2)*(self.grid_size-2),2) 
        
        lat_centroid_dset = fh5.create_dataset('lat_centroid', (self.grid_size, self.grid_size), dtype='float32',fillvalue=np.nan, compression="lzf")
        lon_centroid_dset = fh5.create_dataset('lon_centroid', (self.grid_size, self.grid_size), dtype='float32',fillvalue=np.nan, compression="lzf")
        
        for row,col in centroids_index:
            try:
                lat_points = lat_dset[row:row+2,col:col+2] #gets 4 points
                lat_mean = lat_points.mean()
                lon_points = lon_dset[row:row+2,col:col+2] #gets 4 points
                lon_mean = lon_points.mean()
                if not np.isnan(lat_mean):
                    lat_centroid_dset[row, col] = lat_mean
                    lon_centroid_dset[row, col] = lon_mean
                if row % 250 == 0 and col == self.grid_size/2:
                    #pdb.set_trace()
                    logging.debug('on row: {0} col: {1}'.format(row,col))
                    logging.debug('flushing hdf5')
                    fh5.flush()
            except ValueError:
                pdb.set_trace()
                logging.error('somthing went wrong when making centroids')
        fh5.flush()
        fh5.close()
        logging.debug('exiting function: make_centroids')
        
    def create_centroid_cartesian(self):      
    
        """
        converts centroids from lat,lon to a Lambert azumithal equal area projection
        """
        logging.debug('converting centroids to cartesian coordinates')
        
        fh5 = h5py.File(self.hdf5_name, "r+")
        lat_centroid_dset = fh5.get('lat_centroid')
        lon_centroid_dset = fh5.get('lon_centroid')
        y_centroid_dset = fh5.create_dataset('y_centroid', (self.grid_size, self.grid_size), dtype='float64', compression="lzf")
        x_centroid_dset = fh5.create_dataset('x_centroid', (self.grid_size, self.grid_size), dtype='float64', compression="lzf")
    
    
        #basemap is used to convert points from lat, long to m in x and y. laea projection conserves area
        center = (90.0,0.0)
        m = Basemap(projection='laea',
                    width = 4500000,
                    height = 4000000,
                    resolution='c',lat_0=center[0],lon_0=center[1])
        #pdb.set_trace()
        
        for idx in np.arange(1,lat_centroid_dset.shape[0]):
            if idx % 250 == 0:
                logging.debug('on row: {0} '.format(idx))
                logging.debug('flushing hdf5')
                fh5.flush()
            lat_row = lat_centroid_dset[idx,:]
            lon_row = lon_centroid_dset[idx,:]
            x, y = m(lon_row, lat_row)
            x[x == 1e+30] = np.nan #replace with nan
            y[y == 1e+30] = np.nan #replace with nan
            x_centroid_dset[idx,:],y_centroid_dset[idx,:] = x,y #given in meters
        fh5.flush()
        fh5.close()
        logging.debug('exiting function: create_centroid_cartesian')
    
    
    def make_areas(self):
         
        """
        making areas for each grid cell, starting with:
        the 2nd row, 2nd column, 
        ending with:
        the 2nd to last row, 
        2nd to last column.
        """     
        logging.debug('making area')
        fh5 = h5py.File(self.hdf5_name, "r+")
        yy = fh5.get('y_centroid')
        xx = fh5.get('x_centroid')
        areas_dset = fh5.create_dataset('areas', (self.grid_size, self.grid_size), dtype='float64', compression="lzf")
    
        index_array  = np.mgrid[1:self.grid_size-1,
                                1:self.grid_size-1].swapaxes(0,2).swapaxes(0,1)
        areas_index = index_array.reshape((self.grid_size-2)*(self.grid_size-2),2)
        #pdb.set_trace()
        
        for row, col in areas_index:
            try:
                inp_x = [xx[row,col-1], xx[row,col], xx[row-1,col], xx[row-1,col-1]]
                inp_y = [yy[row,col-1], yy[row,col], yy[row-1,col], yy[row-1,col-1]]       
                if not (np.isnan(np.sum(inp_x)) or np.isnan(np.sum(inp_y))):
                    areas_dset[row,col] = self.polygon_area(inp_x,inp_y)
            except:
    
                pdb.set_trace()   
                logging.error('somthing went wrong when making areas') 
        
        fh5.flush()
        fh5.close()
        logging.debug('exiting function: make_areas')
      
    def polygon_area(self,x,y):                     
        """shoestring formula is applied
        for points centered around row,col
        """
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/(10**6) #converted  from m^2 into km^2    
    
    def make_no_snow_map(self,no_snow_map_name, save=False): 
        """
        Make a .png that shows what your map looks like without snow or
        ice. Used to check if projection looks OK, but is currently not unit 
        tested.
        """
        filename = no_snow_map_name
        logging.debug('getting map with no snow and ice, used for uncompressed plots, as they don\'t distinguish between land and sea')                
        logging.debug('reading file: {}'.format(filename))

        with open(os.path.join(self.data_dir,filename), 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            threashold = 75
            for i, line in enumerate(lines[0:100]): 
                if re.search('0{30,}', line):
                    logging.info('data found at index: {}'.format(i))
                    #header = lines[0:i-1]
                    body = lines[i:-1]
                    break                    
                    break
                if i > threashold:
                    logging.error('cant distinguish header for filename: {}'.format(filename))
                    break
            int_body = body #prevents altering the recursion
            for i, line in enumerate(body):
                
                line = line.replace('3','1') #ice and and snow is changed to sea and land respectively
                line = line.replace('4','2')
                int_body[i] = [int(c) for c in line]
                

                
        def rbg_convert(x):
            snow = (5,5,5)            
            terra = (0,128,0)
            sea = (0,0,139)
            ice = (24,25,26)
            firmament = (0,0,0)            
            
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
        
        no_snow_matrix = np.matrix(int_body)
        #no_snow_matrix = np.fliplr(no_snow_matrix)
        rbg_no_snow_matrix = map(rbg_convert, no_snow_matrix.flat)

        self.rbg_no_snow_matrix = np.array(rbg_no_snow_matrix,dtype='uint16').reshape((self.grid_size,self.grid_size,3))
        
        plt.ioff()
        plt.figure()
        plt.imshow(self.rbg_no_snow_matrix)
        filename = filename.strip('.asc')
        figure_name = os.path.join(self.data_dir,filename+'.png')
        if save:
            plt.savefig(figure_name)
        plt.close()
                

    def make_region_df(self):
        
        return 0

if __name__ == '__main__':
    # create a logging format
#    logger = logging.getLogger(__name__)
#    logger.setLevel(logging.INFO)
#    
#    # create a file handler
#    handler = logging.FileHandler('grid_and_area_4.log')
#    handler.setLevel(logging.INFO)
#    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#    handler.setFormatter(formatter)
    
    # add the handlers to the logger
    #logger.addHandler(handler)
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,filename='grid_and_area.log',level=logging.DEBUG)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()

    data_dir = os.path.join(home_dir,'data')
    output_dict = get_4x4_param()
        
    grid_size = output_dict['grid_size']
    no_snow_planet_name = output_dict['no_snow_planet_name']
    lat_grid_filename = output_dict['lat_grid_filename']
    lon_grid_filename = output_dict['lon_grid_filename']
    lat_long_area_filename = output_dict['lat_long_area_filename']

    #initialize h5 
    ga = grid_and_area(lat_long_area_filename,
             data_dir,
             lat_grid_filename,
             lon_grid_filename,
             grid_size)

    #make centroids 
    ga.make_centroids()
    
    #make cartesian centroid coordinates
    ga.create_centroid_cartesian()
    
    #make areas    
    ga.make_areas()

    ga.make_no_snow_map(no_snow_planet_name, save=True)
#    #play with the hdf5
#    fh5 = h5py.File(os.path.join(data_dir,lat_long_area_filename), "r")
#    areas = fh5.areas
#    lon = np.array(fh5['lon']).flatten()
#    lat = np.array(fh5['lat']).flatten()
    
    
    #fh5.close()
    

