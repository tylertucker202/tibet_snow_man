# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:20:16 2017

@author: tyler
"""
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import os

def get_tibet_24x24_param():
    output_dict = {}
    output_dict['ftp_filename'] = '24km'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_long_area_filename'] = 'lat_long_centroids_area_24km.csv' 
    output_dict['grid_size'] = 1024
    output_dict['lat_long_coords'] = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    output_dict['filename'] = 'Tibet-24km'
    return output_dict
    
def get_sierras_24x24_param():
    no_snow_planet_name = 'dry_planet_24km.asc'
    lat_grid_filename = 'imslat_24km.bin'
    lon_grid_filename = 'imslon_24km.bin'
    lat_long_area_filename = 'sierras_lat_long_centroids_area_24km.csv' 
    grid_size = 1024
    lat_long_coords = {'lower_lat':35,'upper_lat':42,'lower_long':-121,'upper_long':-117} #set as lower and upper bounds for lat and long
    filename = 'sierras_24km'
    return (filename, grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename,lat_long_coords)    

def get_alps_24x24_param():
    no_snow_planet_name = 'dry_planet_24km.asc'
    lat_grid_filename = 'imslat_24km.bin'
    lon_grid_filename = 'imslon_24km.bin'
    lat_long_area_filename = 'alps_lat_long_centroids_area_24km.csv' 
    grid_size = 1024
    lat_long_coords = {'lower_lat':43,'upper_lat':48.5,'lower_long':5,'upper_long':15} #set as lower and upper bounds for lat and long
    filename = 'sierras_24km'
    return (filename, grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename,lat_long_coords)    

def get_alberta_24x24_param():
    no_snow_planet_name = 'dry_planet_24km.asc'
    lat_grid_filename = 'imslat_24km.bin'
    lon_grid_filename = 'imslon_24km.bin'
    lat_long_area_filename = 'alberta_lat_long_centroids_area_24km.csv' 
    grid_size = 1024
    lat_long_coords = {'lower_lat':47,'upper_lat':60,'lower_long':-120,'upper_long':-110} #set as lower and upper bounds for lat and long
    filename = 'Alberta-24km'
    return (filename, grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename,lat_long_coords)    


def get_sierras_4x4_param():
    no_snow_planet_name = 'dry_planet_4km.asc'
    lat_grid_filename = 'imslat_4km.bin'
    lon_grid_filename = 'imslon_4km.bin'
    lat_long_area_filename = 'sierras_lat_long_centroids_area_4km.csv' 
    grid_size = 6144
    lat_long_coords = {'lower_lat':35,'upper_lat':42,'lower_long':-121,'upper_long':-117} #set as lower and upper bounds for lat and long
    filename = 'Sierras-4km'
    return (filename, grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename,lat_long_coords)    
    
def get_tibet_4x4_param():
    output_dict = {}
    output_dict['ftp_filename'] = '4km'
    output_dict['no_snow_planet_name'] = 'dry_planet_4km.asc'
    output_dict['lat_grid_filename'] = 'imslat_4km.bin'
    output_dict['lon_grid_filename'] = 'imslon_4km.bin'
    output_dict['lat_long_area_filename'] = 'lat_long_centroids_area_4km.csv' 
    output_dict['grid_size'] = 6144
    output_dict['lat_long_coords'] = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    output_dict['filename'] = 'Tibet-4km'    
    return output_dict
    
def plot_basemap(filename, lat_long_coords, show = True, save = True):
    
    #make map
    fig = plt.figure(2)
    long_center, lat_center = ((lat_long_coords['upper_long']-lat_long_coords['lower_long'])/2+lat_long_coords['lower_long'],(lat_long_coords['upper_lat']-lat_long_coords['lower_lat'])/2+lat_long_coords['lower_lat'])
    
    m = Basemap(projection='laea',
                width = 4500000,
                height = 4000000,
                resolution='c',lat_0=lat_center,lon_0=long_center)
    x, y = m(long_center, lat_center) # this function converts degrees to meters on this reference map
    top_left = m(lat_long_coords['lower_long'],lat_long_coords['upper_lat'])
    top_right = m(lat_long_coords['upper_long'],lat_long_coords['upper_lat'])
    bottom_left = m(lat_long_coords['lower_long'],lat_long_coords['lower_lat'])
    bottom_right = m(lat_long_coords['upper_long'],lat_long_coords['lower_lat'])
    print('center point x: {} meters'.format(x))
    print('center point y: {} meters'.format(y))
    m.plot(x, y, marker='D',color='cyan')
    m.plot(top_left[0],top_left[1], marker='D',color='cyan')
    m.plot(top_right[0], top_right[1], marker='D',color='cyan')
    m.plot(bottom_left[0], bottom_left[1], marker='D',color='cyan')
    m.plot(bottom_right[0], bottom_right[1], marker='D',color='cyan')
    m.bluemarble()
    if show:
        plt.show()
    if save:
        plot_dir = os.path.join(os.getcwd(),'plots')
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        o
        plt.close()
    return fig