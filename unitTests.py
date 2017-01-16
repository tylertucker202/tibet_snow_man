# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 22:04:10 2016

@author: tyler
"""
import unittest
import os
from generate_grid_and_area import grid_and_area
import math
import numpy as np

class grid_and_area_unit_tests(unittest.TestCase):

    #unless the project structure changes, this should remain unchanged.
    def setUp(self):
        print('unit tests. setUp function called.')   
        self.home_dir = os.getcwd()
        self.data_dir = self.home_dir+'/data/'
        self.no_snow_planet_name =  'dry_planet_24km.asc'
        self.lat_grid_filename = 'imslat_24km.bin'
        self.lon_grid_filename = 'imslon_24km.bin'
        self.lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
        self.grid_size = 1024
        

    def test_init(self):   
        print('Inside test_init') 
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        df = grid_maker.df
        
        self.assertEqual( df.columns.tolist(), ['lat', 'long'], 'df columns not set up properly')
        self.assertEqual( df.count()['lat'], 0,'set should be empty')
        self.assertEqual( df.count()['long'], 0,'set should be empty')
        self.assertEqual( df.shape[0], self.grid_size**2, 'size should be grid_size squared')
        
        centroids = grid_maker.centroids
        
        self.assertEqual( centroids.columns.tolist(),['lat', 'long', 'centroid_lat', 'centroid_long'], 'df columns not set up properly')
        self.assertEqual( centroids.count()['lat'], 0,'set should be empty')
        self.assertEqual( centroids.count()['long'], 0,'set should be empty')
        self.assertEqual( centroids.count()['centroid_lat'], 0,'set should be empty')
        self.assertEqual( centroids.count()['centroid_long'], 0,'set should be empty')
        self.assertEqual( centroids.shape[0], self.grid_size**2, 'size should be grid_size squared')
        self.assertEqual( centroids.shape[0], self.grid_size**2, 'size should be grid_size squared')

    def test_addLatLong(self):
        print('Inside test_addLatLong') 
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        grid_maker.addLatLong(self.lat_grid_filename,self.lon_grid_filename)
        df = grid_maker.df
        
        self.assertNotEqual( df.sum()['lat'], 0,'set should not be empty')
        self.assertNotEqual( df.sum()['long'], 0,'set should not be empty')
        
        self.assertEqual( round(df.sum()['lat'],9), 19465557.748575006,'lat should add up to 19465557.748575006')
        self.assertEqual( round(df.sum()['long'],6), 1654.997860,'long should add up to 1654.997860')
        
        self.assertEqual( round(df.max()['lat'],6), 89.998344,'lat max should be 89.998344')
        self.assertEqual( round(df.max()['long'],6), 179.999741,'long max should be 179.999741')
        
        self.assertEqual( round(df.min()['lat'],6), 0.000004,'lat min should be 0.000004')
        self.assertEqual( round(df.min()['long'],6), -179.999893,'long min should be -179.999893')


    def test_reduceLatLong(self):
        print('Inside test_reduceLatLong') 
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        grid_maker.addLatLong(self.lat_grid_filename,self.lon_grid_filename)
        grid_maker.reduceLatLong()
        
        self.assertEqual(grid_maker.col_max,831,'col max should be 831')
        self.assertEqual(grid_maker.row_max,538,'row max should be 538')
        self.assertEqual(grid_maker.col_min,683,'col min should be 683')
        self.assertEqual(grid_maker.row_min,328,'row min should be 328')
        
    def test_makeCentroids(self):
        print('Inside test_makeCentroids')
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        grid_maker.addLatLong(self.lat_grid_filename,self.lon_grid_filename)
        grid_maker.reduceLatLong()
        grid_maker.makeCentroids()
        
        col,row = (700,400)     
        
        
        ul_lat = grid_maker.centroids.ix[(col,row)].lat
        ur_lat = grid_maker.centroids.ix[(col,row+1)].lat
        bl_lat = grid_maker.centroids.ix[(col+1,row)].lat
        br_lat = grid_maker.centroids.ix[(col+1,row+1)].lat
        
        cent_lat = grid_maker.centroids.ix[(col,row)].centroid_lat
        mean_lat = np.mean([ul_lat,ur_lat,bl_lat,br_lat] )
        
        self.assertEqual(cent_lat, mean_lat, 'centroids are not matched with row, col. Check order of operations' )                
        ul_long = grid_maker.centroids.ix[(col,row)].long
        ur_long = grid_maker.centroids.ix[(col,row+1)].long
        bl_long = grid_maker.centroids.ix[(col+1,row)].long
        br_long = grid_maker.centroids.ix[(col+1,row+1)].long

        cent_long = grid_maker.centroids.ix[(col,row)].centroid_long
        mean_long = np.mean([ul_long,ur_long,bl_long,br_long] )
        
        self.assertEqual(cent_long, mean_long )

    def test_addAreas(self):
        print('Inside test_getAreas') 
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        grid_maker.addLatLong(self.lat_grid_filename,self.lon_grid_filename)
        grid_maker.reduceLatLong()
        grid_maker.addAreas()

        def PolyArea(x,y):
            return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/(10**6)


        col,row = (700,400)  
        
        lr_long = grid_maker.df.ix[(col,row)].x
        ur_long = grid_maker.df.ix[(col,row-1)].x
        ul_long = grid_maker.df.ix[(col-1,row-1)].x
        ll_long = grid_maker.df.ix[(col-1,row)].x
        
        lr_lat = grid_maker.df.ix[(col,row)].y
        ur_lat = grid_maker.df.ix[(col,row-1)].y
        ul_lat = grid_maker.df.ix[(col-1,row-1)].y
        ll_lat = grid_maker.df.ix[(col-1,row)].y
        
        x_i = [lr_long, ur_long, ul_long, ll_long]
        y_i = [lr_lat, ur_lat, ul_lat, ll_lat]
        
        area = PolyArea(x_i,y_i)
        self.assertEqual(area, grid_maker.df.ix[(col,row)].area, 'area is not correct for (col, row)')
        
if __name__ == '__main__':
    unittest.main()
