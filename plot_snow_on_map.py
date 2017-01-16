# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 14:23:26 2017

@author: tyler
"""


import os
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap
import datetime

import pdb

class plotSnow:
    def __init__(self,lat_long_filename,lat_long_coords):
        self.lat_long_coords = lat_long_coords
        self.df_lat_long = pd.read_csv('data/'+lat_long_filename)
        self.set_up_grid()

    def makeMap(self,proj='merc'):
        plt.cla()
        coords = self.lat_long_coords
        
        center = ((coords['upper_long']-coords['lower_long'])/2+coords['lower_long'],(coords['upper_lat']-coords['lower_lat'])/2+coords['lower_lat'])
        
        if proj == 'ortho':
            #Due to a document error, you have to set m in terms of llcrnrx, llcrnry, etc.
            m = Basemap(projection=proj,
                        resolution='c', 
                        lat_0 = center[1],
                        lon_0 = center[0])
  
        elif proj == 'geos':
            #lat_0 must be zero
            m = Basemap(projection=proj,
                llcrnrlat=coords['lower_lat'],
                urcrnrlat=coords['upper_lat'],
                llcrnrlon=coords['lower_long'],
                urcrnrlon=coords['upper_long'],
                lat_ts=20,
                resolution='c', 
                lat_0 = 0,
                lon_0 = center[0])        
        else:
            m = Basemap(projection=proj,
                llcrnrlat=coords['lower_lat'],
                urcrnrlat=coords['upper_lat'],
                llcrnrlon=coords['lower_long'],
                urcrnrlon=coords['upper_long'],
                lat_ts=20,
                resolution='c', 
                lat_0 = center[1],
                lon_0 = center[0])

        m.etopo()
        parallels = np.arange(0., 81, 10)
        meridians = np.arange(10, 351, 10)
        m.drawparallels(parallels, labels =[False, True, True, False])
        m.drawmeridians(meridians, labels =[True, False, False, True])
        return m
    
    def snow_and_ice(self,x):
        if x==4 or x==3:
            x=1 
        else: 
            x=0
        return x
    
    def set_up_grid(self):
        
        snow = '#FEFEFE'            
        lat = self.df_lat_long['lat'].values
        lon = self.df_lat_long['long'].values
        m=self.makeMap(proj='merc')
        x,y = m(lon,lat)
        self.grid_x, self.grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]
        #self.grid_x, self.grid_y = np.mgrid[min(x):max(x):len(x)/6, min(y):max(y):len(y)/6]
        self.cmap1 = LinearSegmentedColormap.from_list("my_colormap", (snow, snow), N=6, gamma=1)
        self.points = np.transpose(np.array([x,y]))
 
    def make_plot_from_col(self, df, col, plot_dir = os.getcwd(), axis = None, show = True, save = False):
        year, day = df[col].name.split("_")
        date = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(day))
        title_string = date.strftime('%Y-%m-%d')
        m=self.makeMap('merc')
        data = df[col].apply(self.snow_and_ice)
        grid_z0 = griddata(self.points, data.values, (self.grid_x, self.grid_y), method='linear') #can be nearest, linear, or cubic interpolation
        grid_z0[ grid_z0 != 1 ] = np.nan
        m.contourf(self.grid_x, self.grid_y,grid_z0, latlon=False, cmap = self.cmap1, alpha=1)
        plt.title(title_string,fontsize=16, color = "black")
        if show:
            plt.show()
        if save:
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)
            plt.savefig(plot_dir+col+'.png')
            plt.close()
        return m
            
if __name__ == '__main__':
    plt.ioff()
    lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    output_dir = os.getcwd()+'/output/'+'grid_compare/'
    lat_long_area_filename_24km = 'lat_long_centroids_area_24km.csv'   
    
    csv_to_plot_dir_24km = 'output/24km_test/'
    filename_24km = '24km.csv'
    col_to_plot = '2015_001'

    df_to_plot_24km = pd.read_csv(output_dir+filename_24km)
    
    s_24 = plotSnow(lat_long_area_filename_24km,lat_long_coords)
    
    m_24 = s_24.make_plot_from_col(df_to_plot_24km, col_to_plot)
    
    lat_long_area_filename_4km = 'lat_long_centroids_area_4km.csv'
    
    filename_4km = '4km.csv'
    df_to_plot_4km = pd.read_csv(output_dir+filename_4km)
    s_4km = plotSnow(lat_long_area_filename_4km,lat_long_coords)
    m_4km = s_4km.make_plot_from_col(df_to_plot_4km, col_to_plot)