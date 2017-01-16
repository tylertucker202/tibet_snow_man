# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:19:53 2017

@author: tyler
"""

from generate_grid_and_area import grid_and_area
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
#matplotlib inline

#%%
home_dir = os.getcwd()
data_dir = home_dir+'/data/'
no_snow_planet_name = 'dry_planet_24km.asc'
lat_grid_filename = 'imslat_24km.bin'
lon_grid_filename = 'imslon_24km.bin'
lat_long_area_filename = 'lat_long_area.csv'
lat_long_coords = {'lower_lat':35,'upper_lat':36,'lower_long':85,'upper_long':86} #set as lower and upper bounds for lat and long
grid_size = 1024
grid_maker = grid_and_area(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
grid_maker.addLatLong(lat_grid_filename,lon_grid_filename)
grid_maker.reduceLatLong()
grid_maker.makeNoSnowMap()

#tibet falls approximatly in this region.
grid_maker.addAreas()
df = grid_maker.df
df.reset_index(level = df.index.names, inplace=True)
#%%

centroid_df = df[df['col'] < 765]
area_df = centroid_df[centroid_df['col'] > 760]
centroid_df = centroid_df[ centroid_df['row'] > 444]
area_df = area_df[ area_df['row'] > 445]
#%%
def get_centroid_coords(area_indexes, centroid_df):
    coords = []    
    df = centroid_df.set_index(['col', 'row'])[ ['centroid_lat', 'centroid_long'] ]
    for idx in area_indexes:
        col, row = idx
        item = [(df.ix[ (col-1,row)]['centroid_lat'], df.ix[ (col-1,row)]['centroid_long']),
                (df.ix[ (col,row)]['centroid_lat'], df.ix[ (col-1,row)]['centroid_long']),
                (df.ix[ (col,row-1)]['centroid_lat'], df.ix[ (col-1,row)]['centroid_long']),
                (df.ix[ (col-1,row-1)]['centroid_lat'], df.ix[ (col-1,row)]['centroid_long'])]
        coords.append(item)
    return coords
#get col and row indexes from area_df
area_indexes = area_df[['col', 'row']].values
#return a list containing the centroid coordinates
centroid_polygons = get_centroid_coords(area_indexes, centroid_df)

#make polygon traces out of each centroid_polygons



#%%        
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    