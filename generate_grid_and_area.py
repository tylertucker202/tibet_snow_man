# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 19:00:13 2016
@author: tyler
"""

import os
import pdb
import numpy as np
import re
import matplotlib.pyplot as plt
import pandas as pd
#import matplotlib
import logging
reload(logging) #need to reload in spyder
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap

class grid_and_area:
    def __init__(self,lat_long_coords,data_dir, no_snow_map_name, grid_size):
        logging.debug('initializing object')
        self.grid_size = grid_size
        self.data_dir = data_dir
        self.coords = lat_long_coords
        self.no_snow_map_name = no_snow_map_name
        self.initDataFrames() #this is the dataframes that we want to build
        
    def initDataFrames(self):
        logging.debug('initializing dataframe' )
        #df only contains lat, long, areas
        #nxn grid is indexed by row and column, thus a multiIndex method is used.
        index = []
        for col in range(0, self.grid_size):
            for row in range(0,self.grid_size):
                index.append((col,row))
        df_index = pd.MultiIndex.from_tuples(index, names = ['col','row'])
        self.df = pd.DataFrame(columns = ['lat', 'long'], index = df_index)
        self.centroids = pd.DataFrame(columns = ['lat', 'long', 'centroid_lat', 'centroid_long'], index = df_index)
        
    def addLatLong(self, lat_filename,long_filename):
        logging.debug('getting Latitude and Longitude arrays:' )
        path = self.data_dir                                  
        try: 
            with open(path+lat_filename, "r") as f:
                lat_array = np.fromfile(f, dtype=np.float32)               
                #list starts at bottom left corner. need to rearrange
                lat_l = lat_array.tolist()
                #chunks are arrays of arrays, each haveing length grid_size,
                #This is later used in getAreas function.                
                lat_chunks = [lat_l[x:x+self.grid_size] for x in xrange(0, len(lat_l), self.grid_size)]
                lat_flat = [item for sublist in lat_chunks[::-1] for item in sublist[::-1]]
                self.df['lat'] = lat_flat
                logging.debug('lat array loaded')
                self.centroids['lat'] = lat_flat
                self.lat_chunks = lat_chunks
            with open(path+long_filename, "r") as f:
                long_array = np.fromfile(f, dtype=np.float32)
                long_l = long_array.tolist()               
                long_chunks = [long_l[x:x+self.grid_size] for x in xrange(0, len(long_l), self.grid_size)]
                long_flat = [item for sublist in long_chunks[::-1] for item in sublist[::-1]]
                self.df['long'] = long_flat
                logging.debug('long array loaded')
                self.centroids['long'] = long_flat
                self.long_chunks = long_chunks
        except:
            pdb.set_trace()
            logging.error('files were not loaded...check path?')
            
            
    def reduceLatLong(self):
        #filter accordingly
        self.df = self.df[ self.df['lat'] >= self.coords['lower_lat'] ]
        self.df = self.df[ self.df['lat'] <= self.coords['upper_lat'] ]
        self.df = self.df[ self.df['long'] >= self.coords['lower_long'] ]
        self.df = self.df[ self.df['long'] <= self.coords['upper_long'] ]
        
        self.lat_long_indicies = self.df.index.tolist()
        
        #get max and min of row and column
        self.df.reset_index(level = self.df.index.names, inplace = True)
        self.col_max = self.df['col'].max()
        self.row_max = self.df['row'].max()
        self.col_min = self.df['col'].min()
        self.row_min = self.df['row'].min()
        self.df.set_index(['col', 'row'], inplace = True)
        

    def makeCentroids(self):
        
        #find centroids for points that fall within lat_long_coords
        index_array = np.mgrid[self.col_min-1:self.col_max+2,self.row_min-1:self.row_max+2].swapaxes(0,2).swapaxes(0,1)
        centroids_index = [item for sublist in index_array for item in sublist.tolist()]
  
        
        #drop all lat,long indicies
        self.centroids = self.centroids.dropna(axis = 0, how='all')
        #reduce centroids to include window around self.coords
        self.centroids.reset_index(level = self.centroids.index.names, inplace = True)
        self.centroids = self.centroids[ (self.centroids['col'] >= self.col_min-1) &
                                         (self.centroids['col'] <= self.col_max+2) &
                                         (self.centroids['row'] >= self.row_min-1) &
                                         (self.centroids['row'] <= self.row_max+2) ]  
        self.centroids.set_index(['col', 'row'], inplace = True)
        
        lat_matrix = self.centroids['lat'].unstack(level=0).values
        long_matrix = self.centroids['long'].unstack(level=0).values
        
        self.centroids.drop( [u'lat',u'long'], axis = 1 ,inplace=True )
        
        for col_abs,row_abs in centroids_index:
            try:
                row = row_abs-self.row_min+1
                col = col_abs-self.col_min+1
                self.centroids.at[(col_abs,row_abs), 'centroid_lat'] = np.mean([ lat_matrix[row,col],lat_matrix[row+1,col],lat_matrix[row,col+1],lat_matrix[row+1,col+1] ])
                self.centroids.at[(col_abs,row_abs), 'centroid_long'] = np.mean([ long_matrix[row,col],long_matrix[row+1,col],long_matrix[row,col+1],long_matrix[row+1,col+1] ]) 
            except:
                self.centroids.ix[(col_abs,row_abs)]
                pdb.set_trace()
                
    def PolyArea(self,x,y):                     
        #shoestring formula is applied for for points centered around row,col
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/(10**6) #converted  from m^2 into km^2
        
    def makeAreas(self):
        
        #shoestring formula is applied for for points centered around row,col
        def PolyArea(x,y):
            return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/(10**6) #converted  from m^2 into km^2

        
        xx = self.centroids['x'].unstack(level=0).values
        yy = self.centroids['y'].unstack(level=0).values
        
        for col_abs,row_abs in self.lat_long_indicies:
            row = row_abs-self.row_min+1
            col = col_abs-self.col_min+1
            #pdb.set_trace()
            try:
                inp_x = [xx[row,col-1], xx[row,col], xx[row-1,col], xx[row-1,col-1]]
                inp_y = [yy[row,col-1], yy[row,col], yy[row-1,col], yy[row-1,col-1]]
                self.centroids.at[(col_abs,row_abs), 'area'] = self.PolyArea(inp_x,inp_y)
            except:

                pdb.set_trace()   
                self.centroids.ix[(col_abs,row_abs)]
    
    def addAreas(self):      

        #basemap is used to convert points from lat, long to m in x and y. laea projection conserves area
        center = ((self.coords['upper_long']-self.coords['lower_long'])/2+self.coords['lower_long'],(self.coords['upper_lat']-self.coords['lower_lat'])/2+self.coords['lower_lat'])
        m = Basemap(projection='laea',
                    width = 4500000,
                    height = 4000000,
                    resolution='c',lat_0=center[1],lon_0=center[0])        
        #convert midpoints to meters


        #self.getCentroids('centroids.csv') #its so much faster, this may no longer be needed
 
        self.makeCentroids()
        #self.centroids = self.centroids[np.isfinite(self.centroids['centroid_long']) & np.isfinite(self.centroids['centroid_lat']) ]
        
        x,y = m(self.centroids['centroid_long'].values, self.centroids['centroid_lat'].values) #given in meters
     
        self.centroids['x'] = x
        self.centroids['y'] = y
        self.makeAreas()
        
        self.df = pd.concat([self.df, self.centroids], axis=1, join_axes=[self.df.index], join='inner' )       
        
    def makeNoSnowMap(self):  
        #Make a .png that shows what your map looks like without snow or
        #ice. Used to check if projection looks OK, but is currently not unit 
        #tested.
        filename = self.no_snow_map_name
        path = self.data_dir
        logging.debug('getting map with no snow and ice, used for uncompressed plots, as they don\'t distinguish between land and sea')                
        logging.debug('reading file: {}'.format(filename))

        with open(path+os.path.join(filename), 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            threashold = 75
            for i, line in enumerate(lines[0:100]): 
                if re.search('0{30,}', line):
                    logging.info('data found at index: {}'.format(i))
                    header = lines[0:i-1]
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
        no_snow_matrix = np.fliplr(no_snow_matrix)
        rbg_no_snow_matrix = map(rbg_convert, no_snow_matrix.flat)

        self.rbg_no_snow_matrix = np.array(rbg_no_snow_matrix,dtype='uint16').reshape((self.grid_size,self.grid_size,3))

        plt.ioff()
        plt.figure()
        plt.imshow(self.rbg_no_snow_matrix)
        filename = filename.strip('.asc')
        figure_name = path+filename+'.png'
        plt.savefig(figure_name)
        plt.close()
                
        self.df['noSnowMap'] = list(map(lambda x: no_snow_matrix[x], self.lat_long_indicies))
        self.df['noSnowMapRBG'] = list(map(lambda x: self.rbg_no_snow_matrix[x], self.lat_long_indicies))

    

    

def get_24x24_param():
    no_snow_planet_name = 'dry_planet_24km.asc'
    lat_grid_filename = 'imslat_24km.bin'
    lon_grid_filename = 'imslon_24km.bin'
    lat_long_area_filename = 'lat_long_centroids_area_24km.csv' 
    grid_size = 1024
    return (grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename)    
    
def get_4x4_param():
    no_snow_planet_name = 'dry_planet_4km.asc'
    lat_grid_filename = 'imslat_4km.bin'
    lon_grid_filename = 'imslon_4km.bin'
    lat_long_area_filename = 'lat_long_centroids_area_4km.csv'    
    grid_size = 6144
    return (grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename)    

if __name__ == '__main__':
    logging.basicConfig(filename='grid_and_area.log',level=logging.WARNING)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()
    data_dir = home_dir+'/data/'
    
    grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename = get_24x24_param()
    #grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename = get_4x4_param()

    lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    
    #initialize object
    
    grid_maker = grid_and_area(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
    
    logging.info('make lat long, and area dataframe')
    
    grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
    grid_maker.reduceLatLong()
    grid_maker.makeNoSnowMap()
        
    #tibet falls approximatly in this region.
    grid_maker.addAreas()
    
    grid_maker.df.to_csv(data_dir+lat_long_area_filename) 
    asdf = grid_maker.df[ grid_maker.df['area'] < 100]

    

    