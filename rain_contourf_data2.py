# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 18:55:53 2016

@author: tyler
"""
import os
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

import pdb

lat_min=25
lat_max=45
lon_min=65
lon_max=105

#make map
def makeMap():
    plt.cla()
    coords = {'lower_lat':lat_min-2,'upper_lat':lat_max+2,'lower_long':lon_min-2,'upper_long':lon_max+2} #set as lower and upper bounds for lat and long
    center = ((coords['upper_long']-coords['lower_long'])/2+coords['lower_long'],(coords['upper_lat']-coords['lower_lat'])/2+coords['lower_lat'])
    
    m = Basemap(projection='merc',
                llcrnrlat=coords['lower_lat'],
                urcrnrlat=coords['upper_lat'],
                llcrnrlon=coords['lower_long'],
                urcrnrlon=coords['upper_long'],
                lat_ts=20,
                resolution='c')            
    #m.drawcoastlines()
    # draw a boundary around the map, fill the background.
    # this background will end up being the ocean color, since
    # the continents will be drawn on top.
    #m.drawmapboundary(fill_color='None')
    # fill continents, set lake color same as ocean color.
    #m.fillcontinents(color='None',lake_color='aqua')
    m.bluemarble()                   
    #m.shadedrelief()
    #m.etopo()
    parallels = np.arange(0., 81, 5)
    meridians = np.arange(10, 351, 5)
    m.drawparallels(parallels, labels =[False, True, True, False])
    m.drawmeridians(meridians, labels =[True, False, True, False])
    return m

def time_and_space_filter(df, start, end, lat_min, lat_max, lon_min, lon_max):      
    df = df[ (df['Lat'] >= lat_min) & (df['Lat'] <= lat_max) & (df['Lon'] >= lon_min) & (df['Lon'] <= lon_max)]
    start_idx = [ i for i, word in enumerate(df.columns) if word.endswith(start) ]
    end_idx = [ i for i, word in enumerate(df.columns) if word.endswith(end) ]
    output_df = pd.concat( [df[ ['Lat','Lon']], df[ range(start_idx[0], end_idx[0]+1)] ] , axis = 1)
    return(output_df)  

#%%
#get dataframe
df = pd.read_csv('/home/tyler/Desktop/MATH636/team_project/proj/data/sogpm2P5V1.0.csv')
start = '01_1998'
end = '12_2009'
df_filtered = time_and_space_filter(df, start, end, lat_min, lat_max, lon_min, lon_max) 
lat = df_filtered['Lat'].values
lon = df_filtered['Lon'].values
df_filtered = df_filtered.drop( ['Lat','Lon'], 1)

m=makeMap()
x,y = m(lon,lat)
points = np.transpose(np.array([x,y]))
grid_x, grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]
cmap = plt.cm.get_cmap("jet")


cmap = plt.cm.get_cmap("jet")
plt.close()
points = np.transpose(np.array([x,y]))
grid_x, grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]

plt.ioff()

fig = plt.figure(figsize=(8, 8))

ax1 = fig.add_axes([0.05, 0.07, 0.9, 0.03])
norm = mpl.colors.Normalize(vmin=df_filtered.min().min(), vmax=df_filtered.max().max())
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('mm/day')

for col in df_filtered.columns:
    data = df_filtered[col]
    month, year = col.split("_")

    
    title_string = r"Year: "+year+" Month: "+month
    ax2 = fig.add_axes([0.00, .15, 1, 0.70])
    m=makeMap()
    grid_z0 = griddata(points, data.values, (grid_x, grid_y), method='linear') #can be nearest, linear, or cubic interpolation
    m.contourf(grid_x, grid_y,grid_z0,cmap = cmap, latlon=False, vmin=df_filtered.min().min(), vmax=df_filtered.max().max(), alpha = .5)
    plt.title(title_string,fontsize=16, color = "black", y=1.08)
    plt.savefig('/home/tyler/Desktop/MATH636/tibet_snowpack/prec_images/'+year+'_'+month+'.png')
    #pdb.set_trace()
    #plt.close()
    
#%%

df = pd.read_csv('/home/tyler/Desktop/MATH636/team_project/proj/data/sogpm2P5V1.0.csv')

start = '01_1998'
end = '12_2009'

lat = df['Lat'].values
lon = df['Lon'].values
m=makeMap()
x,y = m(lon,lat)
points = np.transpose(np.array([x,y]))
grid_x, grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]
cmap = plt.cm.get_cmap("jet")

df_filtered = time_and_space_filter(df, start, end, lat_min, lat_max, lon_min, lon_max)   
    
data = df_filtered[df_filtered.columns[0]]
#%%
month, year = data.name.split("_")

title_string = r"Year: "+year+" Month: "+month


fig = plt.figure(figsize=(8, 8))

ax1 = fig.add_axes([0.05, 0.07, 0.9, 0.03])
cmap = mpl.cm.get_cmap("winter")
norm = mpl.colors.Normalize(vmin=df.min().min(), vmax=df.max().max())
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('mm/day')

ax2 = fig.add_axes([0.00, .15, 1, 0.70])
m=makeMap()
grid_z0 = griddata(points, data.values, (grid_x, grid_y), method='linear') #can be nearest, linear, or cubic interpolation
m.contourf(grid_x, grid_y,grid_z0, latlon=False, vmin=df.min().min(), vmax=df.max().max(), alpha = .5)

cmapw = plt.cm.get_cmap("winter")
bounds=[df.min().min(),df.max().max()]
values = [df.min().min(),df.max().max()]
norms = mpl.colors.Normalize(vmin=df.min().min(), vmax=df.max().max())
plt.title(title_string,fontsize=16, color = "black", y=1.08)
plt.show()