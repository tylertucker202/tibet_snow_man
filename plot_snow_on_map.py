# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 14:23:26 2017

@author: tyler
"""


import os, glob
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap


import pdb

class plotSnow:
    def __init__(self,data_dir, lat_long_area_filename,lat_long_coords):
        self.lat_long_coords = lat_long_coords
        self.df_lat_long = pd.read_csv(os.path.join(data_dir,lat_long_area_filename))
        self.set_up_grid()

    def make_map(self,proj='merc'):
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
        m=self.make_map(proj='merc')
        x,y = m(lon,lat)
        self.grid_x, self.grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]
        #self.grid_x, self.grid_y = np.mgrid[min(x):max(x):len(x)/6, min(y):max(y):len(y)/6]
        self.cmap1 = LinearSegmentedColormap.from_list("my_colormap", (snow, snow), N=6, gamma=1)
        self.points = np.transpose(np.array([x,y]))

    def make_plots_from_HDFStore(self, output_dir, show = True, save = False):
        plt.ioff()
        file_names = sorted(glob.glob(os.path.join(output_dir,"*.h5")), key = lambda x: x.rsplit('.', 1)[0])
        for f in file_names:
            with pd.HDFStore(f) as year_store:
                for series_name in year_store.keys():
                    
                    timestamp = series_name.strip('/series_')
                    m=self.make_map('merc')
                    data = year_store[series_name].apply(self.snow_and_ice)
                    grid_z0 = griddata(self.points, data.values, (self.grid_x, self.grid_y), method='linear') #can be nearest, linear, or cubic interpolation
                    grid_z0[ grid_z0 != 1 ] = np.nan
                    m.contourf(self.grid_x, self.grid_y,grid_z0, latlon=False, cmap = self.cmap1, alpha=1)
                    plt.title(timestamp,fontsize=16, color = "black")
                    if show:
                        plt.show()
                    if save:
                        plot_dir = os.path.join(output_dir,'plots')
                        if not os.path.exists(plot_dir):
                            os.makedirs(plot_dir)
                        plt.savefig(os.path.join(plot_dir,timestamp+'.png'))
                        plt.close()
        