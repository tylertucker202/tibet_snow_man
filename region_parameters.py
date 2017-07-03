# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 12:20:16 2017

@author: tyler
"""


def get_tibet_24x24_param():
    print('inside get_tibet_24x24_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '24km'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'tibet_test-24km.hdf5'
    output_dict['grid_size'] = 1024
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 25,
                                     'upper_lat': 45,
                                     'lower_lon': 65,
                                     'upper_lon': 105}
    output_dict['filename'] = 'Tibet-24km'

    return output_dict


def get_24x24_param():
    print('inside get_24x24_param')
    output_dict = dict()
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'twenty_four_km_areas.hdf5'
    output_dict['grid_size'] = 1024
    return output_dict


def get_4x4_param():
    print('inside get_4x4_param')
    output_dict = dict()
    output_dict['no_snow_planet_name'] = 'dry_planet_4km.asc'
    output_dict['lat_grid_filename'] = 'imslat_4km.bin'
    output_dict['lon_grid_filename'] = 'imslon_4km.bin'
    output_dict['lat_lon_area_filename'] = 'four_km_areas.hdf5'
    output_dict['grid_size'] = 6144
    return output_dict

def get_1x1_param():
    print('inside get_1x1_param')
    output_dict = dict()
    output_dict['no_snow_planet_name'] = 'dry_planet_1km.asc'
    output_dict['lat_grid_filename'] = 'imslat_1km.bin'
    output_dict['lon_grid_filename'] = 'imslon_1km.bin'
    output_dict['lat_lon_area_filename'] = 'one_km.hdf5'
    output_dict['grid_size'] = 24576
    return output_dict


def get_test_tibet_24x24_param():
    print('inside get_test_tibet_24x24_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '24km_test'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'tibet-test-24km.hdf5'
    output_dict['grid_size'] = 1024
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 25,
                                     'upper_lat': 45,
                                     'lower_lon': 65,
                                     'upper_lon': 105}
    output_dict['filename'] = 'Test-Tibet-24km'

    return output_dict


def get_4_lakes_4x4_param():
    print('inside get_4_lakes_4x4_param')
    output_dict = dict()
    output_dict['grid_size'] = 6144
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 28,
                                     'upper_lat': 34,
                                     'lower_lon': 87.5,
                                     'upper_lon': 92.5}
    output_dict['filename'] = 'Four-Lakes-4km'

    return output_dict

def get_4_lakes_24x24_param():
    print('inside get_4_lakes_24x24_param')
    output_dict = dict()
    output_dict['grid_size'] = 1024
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 28,
                                     'upper_lat': 34,
                                     'lower_lon': 87.5,
                                     'upper_lon': 92.5}
    output_dict['filename'] = 'Four-Lakes-24km'

    return output_dict


def get_sierras_24x24_param():
    print('inside get_sierras_24x24_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '24km'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'sierras_lat_lon_centroids_area_24km.csv'
    output_dict['grid_size'] = 1024
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 35,
                                     'upper_lat': 42,
                                     'lower_lon': -121,
                                     'upper_lon': -117}
    output_dict['filename'] = 'Sierras_24km'

    return output_dict



def get_alps_24x24_param():
    print('inside get_alps_24x24_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '24km'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'alps_lat_lon_centroids_area_24km.csv' 
    output_dict['grid_size'] = 1024
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 43,
                                     'upper_lat': 48.5,
                                     'lower_lon': 5,
                                     'upper_lon': 15}
    output_dict['filename'] = 'Alps-24km'

    return output_dict


def get_alberta_24x24_param():
    print('inside get_alberta_24x24_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '24km'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'alberta_lat_lon_centroids_area_24km.csv' 
    output_dict['grid_size'] = 1024
    # set as lower and upper bounds for lat and long
    output_dict['lat_lon_coords'] = {'lower_lat': 47,
                                     'upper_lat': 60,
                                     'lower_lon': -120,
                                     'upper_lon': -110}
    output_dict['filename'] = 'Alberta-24km'

    return output_dict    


def get_artic_24x24_param():
    
    print('inside get_artic_24x24_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '24km'
    output_dict['no_snow_planet_name'] = 'dry_planet_24km.asc'
    output_dict['lat_grid_filename'] = 'imslat_24km.bin'
    output_dict['lon_grid_filename'] = 'imslon_24km.bin'
    output_dict['lat_lon_area_filename'] = 'artic_lat_lon_centroids_area_24km.csv' 
    output_dict['grid_size'] = 1024
    output_dict['lat_lon_coords'] = {'lower_lat': 65,
                                     'upper_lat': 90,
                                     'lower_lon': -180,
                                     'upper_lon': 180}
    output_dict['filename'] = 'Artic-24km'

    return output_dict


def get_sierras_4x4_param():

    print('inside get_sierras_4x4_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '4km'
    output_dict['no_snow_planet_name'] = 'dry_planet_4km.asc'
    output_dict['lat_grid_filename'] = 'imslat_4km.bin'
    output_dict['lon_grid_filename'] = 'imslon_4km.bin'
    output_dict['lat_lon_area_filename'] = 'sierras_lat_lon_centroids_area_4km.csv' 
    output_dict['grid_size'] = 6144
    output_dict['lat_lon_coords'] = {'lower_lat': 35,
                                     'upper_lat': 42,
                                     'lower_lon': -121,
                                     'upper_lon': -117}
    output_dict['filename'] = 'Sierras-4km'

    return output_dict 


def get_tibet_4x4_param():

    print('inside get_tibet_4x4_param')
    output_dict = dict()
    output_dict['ftp_filename'] = '4km'
    output_dict['no_snow_planet_name'] = 'dry_planet_4km.asc'
    output_dict['lat_grid_filename'] = 'imslat_4km.bin'
    output_dict['lon_grid_filename'] = 'imslon_4km.bin'
    output_dict['lat_lon_area_filename'] = 'tibet_lat_lon_centroids_area_4km.csv' 
    output_dict['grid_size'] = 6144
    output_dict['lat_lon_coords'] = {'lower_lat': 25,
                                     'upper_lat': 45,
                                     'lower_lon': 65,
                                     'upper_lon': 105}
    output_dict['filename'] = 'Tibet-4km'

    return output_dict

