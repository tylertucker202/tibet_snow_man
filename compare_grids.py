# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 21:08:38 2017

@author: tyler
"""

import os
from snowCode import makeSnowDF
from plot_snow_on_map import plotSnow
import pandas as pd
import pdb
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap
import datetime

output_dir = os.getcwd()+'/output/'+'grid_compare/'
home_dir = os.getcwd()
data_dir = home_dir+'/data/'
input_zip_dir_24km = data_dir+'grid_compare/24km/'
lat_long_area_filename_24km = 'lat_long_centroids_area_24km.csv'
lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long


makeDF_24km = makeSnowDF(data_dir,lat_long_area_filename_24km,lat_long_coords)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

df_24km = makeDF_24km.createTimeSeriesDf(input_zip_dir_24km) 
df_24km.to_csv(output_dir+'/24km.csv')


lat_long_area_filename_24km = 'lat_long_centroids_area_24km.csv'   
csv_to_plot_dir_24km = 'output/24km_test/'
filename_24km = '24km.csv'
col_to_plot = '2015_001'

df_to_plot_24km = pd.read_csv(output_dir+filename_24km)

s_24km = plotSnow(lat_long_area_filename_24km,lat_long_coords)

#m_24km = s_24km.make_plot_from_col(df_to_plot_24km, col_to_plot)


df_24km.to_csv(output_dir+'/24km.csv')


#%%
##initialize object
input_zip_dir_4km = data_dir+'grid_compare/4km/'
lat_long_area_filename_4km = 'lat_long_centroids_area_4km.csv'

makeDF_4km = makeSnowDF(data_dir,lat_long_area_filename_4km,lat_long_coords)

df_4 = makeDF_4km.createTimeSeriesDf(input_zip_dir_4km) 
df_4.to_csv(output_dir+'/4km.csv')
df_to_plot_4km = pd.read_csv(output_dir+'/4km.csv')
s_4km = plotSnow(lat_long_area_filename_4km,lat_long_coords)

#m_4km = s_4km.make_plot_from_col(df_to_plot_4km, col_to_plot)

#%%

def make_subplotmake_plot_from_col(df, df_lat_long, col, coords, ax):
    center = ((coords['upper_long']-coords['lower_long'])/2+coords['lower_long'],(coords['upper_lat']-coords['lower_lat'])/2+coords['lower_lat'])

    m = Basemap(projection='merc',
        llcrnrlat=coords['lower_lat'],
        urcrnrlat=coords['upper_lat'],
        llcrnrlon=coords['lower_long'],
        urcrnrlon=coords['upper_long'],
        lat_ts=20,
        resolution='c', 
        lat_0 = center[1],
        lon_0 = center[0], ax = ax)
    m.etopo()
    parallels = np.arange(0., 81, 10)
    meridians = np.arange(10, 351, 10)
    m.drawparallels(parallels, labels =[False, True, True, False])
    m.drawmeridians(meridians, labels =[True, False, False, True])
    
    snow = '#FEFEFE'            
    lat = df_lat_long['lat'].values
    lon = df_lat_long['long'].values
    
    x,y = m(lon,lat)
    grid_x, grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]
    
    cmap1 = LinearSegmentedColormap.from_list("my_colormap", (snow, snow), N=6, gamma=1)
    points = np.transpose(np.array([x,y]))
          
    data = df[col].apply(snow_and_ice)
    grid_z0 = griddata(points, data.values, (grid_x, grid_y), method='linear') #can be nearest, linear, or cubic interpolation
    grid_z0[ grid_z0 != 1 ] = np.nan
    m.contourf(grid_x, grid_y,grid_z0, latlon=False, cmap = cmap1, alpha=1)

    return m
#%%
def snow_and_ice(x):
    if x==4 or x==3:
        x=1 
    else: 
        x=0
    return x        
#%%
fig, ax = plt.subplots(1, 2)

year, day = col_to_plot.split("_")
date = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(day))
title_string = date.strftime('%Y-%m-%d')
plt.suptitle('Comparison of different resolutions on date: {0}'.format(title_string), size = 14)
#fig.set_size_inches(4, 6)

ax[0].set_title("24 km", size = 12)
m_24km = make_subplotmake_plot_from_col(df_to_plot_24km, s_24km.df_lat_long, col_to_plot, lat_long_coords, ax = ax[0])
ax[1].set_title("4 km", size = 12)
m_24km = make_subplotmake_plot_from_col(df_to_plot_4km, s_4km.df_lat_long, col_to_plot, lat_long_coords, ax = ax[1])
plt.show()

#%%
def getPercSnow(df, col):
    data = df[col].apply(snow_and_ice)
    return data.mean(axis = 0)

perc_coverage_24km = getPercSnow(df_to_plot_24km, col_to_plot)
perc_coverage_4km = getPercSnow(df_to_plot_4km, col_to_plot)

perc_diff = (perc_coverage_4km - perc_coverage_24km)/perc_coverage_24km