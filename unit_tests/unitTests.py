# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 22:04:10 2016

@author: tyler
"""
import unittest
import os, glob
import gzip
from generate_grid_and_area import grid_and_area
from plot_snow_on_map import plotSnow
from snowCode import makeSnowHDFStore 
from math import radians, cos, sin, asin, sqrt
import numpy as np
import datetime
import pandas as pd
import pdb
import matplotlib.pyplot as plt

class grid_and_area_unit_tests(unittest.TestCase):

    #unless the project structure changes, this should remain unchanged.
    def setUp(self):
        print('unit tests. setUp function called.')   
        self.home_dir = os.path.join(os.getcwd(),os.pardir)
        self.data_dir = os.path.join(self.home_dir,os.pardir,'data')
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
        
        self.assertEqual( centroids.columns.tolist(),['lat', 'long', 'centroid_lat', 'centroid_long', 'area_points'], 'df columns not set up properly')
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
        
        
        self.assertEqual(grid_maker.row_max,831,'col max should be 831')
        self.assertEqual(grid_maker.col_max,538,'row max should be 538')
        self.assertEqual(grid_maker.row_min,683,'col min should be 683')
        self.assertEqual(grid_maker.col_min,328,'row min should be 328')

#        self.assertEqual(grid_maker.col_max,831,'col max should be 831')
#        self.assertEqual(grid_maker.row_max,538,'row max should be 538')
#        self.assertEqual(grid_maker.col_min,683,'col min should be 683')
#        self.assertEqual(grid_maker.row_min,328,'row min should be 328')
        
    def test_makeCentroids(self):
        print('Inside test_makeCentroids')
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        grid_maker.addLatLong(self.lat_grid_filename,self.lon_grid_filename)
        grid_maker.reduceLatLong()
        grid_maker.makeCentroids()
        
        #col,row = (700,400)     
        row,col = (700,400)  
        #pdb.set_trace()
        ul_lat = grid_maker.df.ix[(col,row)].lat
        ur_lat = grid_maker.df.ix[(col,row+1)].lat
        bl_lat = grid_maker.df.ix[(col+1,row)].lat
        br_lat = grid_maker.df.ix[(col+1,row+1)].lat
        
        cent_lat = grid_maker.centroids.ix[(col,row)].centroid_lat
        mean_lat = np.mean([ul_lat,ur_lat,bl_lat,br_lat] )
        
        self.assertEqual(cent_lat, mean_lat, 'centroids are not matched with row, col. Check order of operations' )                
        ul_long = grid_maker.df.ix[(col,row)].long
        ur_long = grid_maker.df.ix[(col,row+1)].long
        bl_long = grid_maker.df.ix[(col+1,row)].long
        br_long = grid_maker.df.ix[(col+1,row+1)].long

        cent_long = grid_maker.centroids.ix[(col,row)].centroid_long
        mean_long = np.mean([ul_long,ur_long,bl_long,br_long] )
        
        self.assertEqual(cent_long, mean_long)

    def test_addAreas(self):
        print('Inside test_getAreas') 
        grid_maker = grid_and_area(self.lat_long_coords,self.data_dir,self.no_snow_planet_name,self.grid_size)
        grid_maker.addLatLong(self.lat_grid_filename,self.lon_grid_filename)
        grid_maker.reduceLatLong()
        grid_maker.addAreas()


        row,col = (700,400)  
        
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
        
        area = grid_maker.PolyArea(x_i,y_i)
        self.assertEqual(area, grid_maker.df.ix[(col,row)].area, 'area is not correct for (col, row)')
        
        #check if sum of areas is approximate to the exact region.  
        
        df_24km = grid_maker.df
        
        def haversine_formula(lat1, lat2,lon1, lon2):
            """
            Calculate the great circle distance between two points 
            on the earth (specified in decimal degrees)
            """
            # haversine formula 
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            return c
        
        
        def semi_perimeter(d, phi_1, phi_2):
            s = (d  + np.pi  + (phi_1 + phi_2) )* .5
            return s
        
        def lhuilier(s, d, phi_1, phi_2): #uses unit sphere R=1
        
            inner_sq = np.sqrt( np.tan( 0.5*s ) * 
                                np.tan( 0.5*(s-d) ) * 
                                np.tan( 0.5*(s-(np.pi/2 + phi_1)) ) * 
                                np.tan( 0.5*(s-(np.pi/2 + phi_2)) ) )
            ans = 4.0 * np.arctan(inner_sq)
            return ans
        
        
        bottom_phi = 25
        top_phi = 45
        left_lambda = 65
        right_lambda = 105
        
        # convert decimal degrees to radians 
        bottom_phi, top_phi, left_lambda, right_lambda = map(radians, [bottom_phi, top_phi, left_lambda, right_lambda])
        
        R = 6371 #km
        
        d_bottom = haversine_formula(bottom_phi, bottom_phi,left_lambda, right_lambda)
        print('bottom length: {}'.format(R * d_bottom))
        s_bottom = semi_perimeter(d_bottom, bottom_phi, bottom_phi)
        E_bottom = lhuilier(s_bottom, d_bottom, bottom_phi, bottom_phi)
        #E_bottom = lhuilier(R*s_bottom, R*d_bottom, R*bottom_phi, R*bottom_phi,R)
        
        d_top = haversine_formula(top_phi, top_phi,left_lambda, right_lambda)
        print('top length: {}'.format(R * d_top))
        s_top = semi_perimeter(d_top, top_phi, top_phi)
        E_top = lhuilier(s_top, d_top,top_phi, top_phi)
        #E_top = lhuilier(R*s_top, R*d_top,R*top_phi, R*top_phi,R)
        
        
        tibet_area = R**2 * (E_top - E_bottom)
        
        print('tibet area via 24km grid_maker: {}'.format(df_24km['area'].sum()))
        print('tibet area via Haversine formula: {}'.format(tibet_area))
        perc_dif_24 = 100*(df_24km['area'].sum()-tibet_area)/tibet_area
        print('percent difference: {0}'.format(perc_dif_24))
        
        self.assertLess(abs(perc_dif_24), 1, "area does not add up to approximatly to the spherical triangle")
        
class snowCode_unit_tests(unittest.TestCase):

    #unless the project structure changes, this should remain unchanged.
    def setUp(self):
        print('on snowCode_unit_tests. setUp function called.')   
        self.home_dir = os.path.join(os.getcwd(),os.pardir)
        self.data_dir = os.path.join(self.home_dir,os.pardir,'data')
        self.input_zip_dir = os.path.join(self.home_dir,os.pardir,'zip_files','24km_unit_test')
        self.lat_long_area_filename = 'lat_long_centroids_area_24km.csv'
        self.lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long

    def test_init(self):
        #check if the right area dataframe was added
        makeHDF = makeSnowHDFStore(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        self.assertEqual(makeHDF.df.index.size, 20607, 'there should be 20607 points in the tibet dataframe')        
        self.assertEqual( round(makeHDF.df['area'].sum(),4), 8062815.0957, 'total area should be 8062815.0956963645')
        
    def test_build_terrain(self):

        makeHDF = makeSnowHDFStore(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        
        m = [0, 0, 0, 3, 4] #zero represents either space, water or land. 3 and 4 represents ice and snow respectively
        terrain_list = [0, 1, 2, 1, 2] #dumbed down version of the no_snow_map found in self.df['noSnowMap'].values.tolist()
        
        m_with_land_list = map( lambda no_snow_elem,matrix_elem:
                                makeHDF.build_terrain(no_snow_elem,matrix_elem),
                                terrain_list, m)

        correct_m = [0,1,2,3,4]        
        
        self.assertEqual(m_with_land_list, correct_m,'array should equal [0,1,2,3,4] ')        
        
    def test_make_hdf5_files(self):

        makeHDF = makeSnowHDFStore(self.data_dir,
                                   self.lat_long_area_filename,
                                   self.lat_long_coords)
        print('Start parsing through compressed files')
        makeHDF.make_hdf5_files(os.path.join(self.home_dir,self.input_zip_dir))
        

        #An output directory shall exist
        output_dir = os.path.join(os.getcwd(),'output',os.path.basename(self.input_zip_dir))
        self.assertTrue(os.path.exists(output_dir))
        #There shall be two .h5 files in this directory
        files = glob.glob(os.path.join(output_dir,'*.h5'))
        #pdb.set_trace()
        self.assertEqual(len(files),2)
        self.assertEqual(os.path.basename(files[0]),'2000.h5')
        self.assertEqual(os.path.basename(files[1]),'1997.h5')
        #year 1997 .h5 store shall contain three series
        year_store_1997 = pd.HDFStore(files[1])
        self.assertEqual(len(year_store_1997),3)
        #year 2000 .h5 store shall contain two series
        year_store_2000 = pd.HDFStore(files[0])
        self.assertEqual(len(year_store_2000),2)
        
        #file ims1997127_24km_v1.1.asc.gz is alternatively formatted
        #file ims1997035_24km_v1.1.asc.gz is normally formatted        
        nom_formatted_file = '1997/ims1997035_24km_v1.1.asc.gz'
        alt_formatted_file = '1997/ims1997127_24km_v1.1.asc.gz' 

        with gzip.open(os.path.join(self.home_dir,self.input_zip_dir, nom_formatted_file), 'r') as f:
            content = f.read()
            lines = content.split('\n')
            nominally_formatted_bool, body = makeHDF.check_if_nominally_formatted(lines, nom_formatted_file)
            self.assertTrue(nominally_formatted_bool)
            nom_data = makeHDF.parse_normally_formatted_file(body,nom_formatted_file)
            
        with gzip.open(os.path.join(self.home_dir,self.input_zip_dir, alt_formatted_file), 'r') as f:
            content = f.read()
            lines = content.split('\n')
            nominally_formatted_bool, body = makeHDF.check_if_nominally_formatted(lines, alt_formatted_file)
            self.assertFalse(nominally_formatted_bool)
            alt_data = makeHDF.parse_alternatively_formatted_file(body,alt_formatted_file)
        
        def remove_snow_and_ice(x):
            if x == 3:
                x = 1
            if x == 4:
                x = 2
            return x
                
        #replace snow and ice with land. This should be almost to the tibet landscape
        alt_data = map(lambda x: remove_snow_and_ice(x),alt_data)
        nom_data = map(lambda x: remove_snow_and_ice(x),nom_data)
              
        no_snow_df = makeHDF.df['noSnowMap']
        no_snow_land_count = no_snow_df[ no_snow_df == 2].size    
        no_snow_water_count = no_snow_df[ no_snow_df == 1].size
        
        alt_data_land_count = alt_data.count(2)
        alt_data_water_count = alt_data.count(1)
        
        nom_data_land_count = nom_data.count(2)
        nom_data_water_count = nom_data.count(1)
        
        #There is little land
        self.assertEqual(alt_data_land_count , no_snow_land_count,'land count should be equal')  
        self.assertEqual(alt_data_water_count , no_snow_water_count,'water count should be equal') 
        """
        Number of water should approximatly equal 33.
        this test comprimises with a threshold.
        if this test fails, there may be somthing wrong with 
        parse_alternatively_formatted_file or parse_normally_formatted_file
        np.fliplr or np.flipud may be missing.
        """
        error_threashold = 10
        alt_error = abs(alt_data_water_count - no_snow_water_count)
        nom_error = abs(nom_data_water_count - no_snow_water_count)
        
        #data doesn't quite match up       
        self.assertLess(alt_error,error_threashold, 'parse_alternatively_formatted_file function is not matching noSnowMap' )
        self.assertLess(nom_error,error_threashold, 'parse_normally_formatted_file function is not matching noSnowMap' )
        
        #test if time series matches master timeseries

class plotSnow(unittest.TestCase):

    #unless the project structure changes, this should remain unchanged.
    def setUp(self):
        print('on plotSnow_unit_tests. setUp function called.')   
        self.home_dir = os.path.join(os.getcwd(),os.pardir)
        self.data_dir = os.path.join(self.home_dir,os.pardir,'data')
        self.input_zip_dir = os.path.join(self.home_dir,os.pardir,'zip_files','24km_unit_test')
        self.lat_long_area_filename = 'lat_long_centroids_area_24km.csv'
        self.lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
        self.output_dir = os.path.join(os.getcwd(),'output',os.path.basename(self.input_zip_dir))
        
    def test_init(self): 
        
        print('on test_init')
        from plot_snow_on_map import plotSnow #needs to reload this here (possible unit test bug?)
        plotHDF = plotSnow(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        self.assertEqual(plotHDF.lat_long_coords, self.lat_long_coords, 'check lat-long coords')
        self.assertEqual(plotHDF.df_lat_long.shape, (20607,13), 'check df')
        
    def test_make_map(self):
        print('on test_make_map')
        from plot_snow_on_map import plotSnow #needs to reload this here (possible unit test bug?)
        plotHDF = plotSnow(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        m = plotHDF.make_map(proj='merc')
        
        self.assertEqual(m.latmax, 45.0, 'check latitude')
        self.assertEqual(m.latmin, 25.0, 'check latitude')
        self.assertEqual(m.lonmax, 105.0, 'check longitude')
        self.assertEqual(m.lonmin, 65.0, 'check longitude')
        self.assertEqual(round(m.xmax,3), 4179560.113, 'check xmax')
        self.assertEqual(round(m.ymax,3), 2577297.868, 'check ymax')

        
        
    def test_snow_and_ice(self):
        print('on test_snow_and_ice')  
        test_array = [0,1,2,3,4]  
        expected_output = [0,0,0,1,1]
        
        from plot_snow_on_map import plotSnow #needs to reload this here (possible unit test bug?)
        plotHDF = plotSnow(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        actual_output = map(lambda x: plotHDF.snow_and_ice(x), test_array)
        self.assertEqual(actual_output, expected_output, 'check snow_and_ice function')
        
        
    def test_set_up_grid(self):
        print('on test_set_up_grid')  

        from plot_snow_on_map import plotSnow #needs to reload this here (possible unit test bug?)
        plotHDF = plotSnow(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        plotHDF.set_up_grid()
        
        self.assertEqual(plotHDF.grid_x.shape, (3000,3000), 'check grid_x')
        first_point = np.array([17276.655 ,2565167.345])

        #last_point = np.array([4.06924128e+06,3.48765474e+02])
        
        self.assertEqual(plotHDF.points[0].round(3)[0], first_point[0], 'check points')
        self.assertEqual(plotHDF.points[0].round(3)[1], first_point[1], 'check points')
        
        
    def test_make_plots_from_HDFStore(self):
        print('on test_make_plots_from_HDFStore')
        print('this method does not automatically verify, you have to check the images yourself')

        #first make hdf5 database using unitTest directory
        makeHDF = makeSnowHDFStore(self.data_dir,
                                   self.lat_long_area_filename,
                                   self.lat_long_coords)
        print('Start parsing through compressed files')
        makeHDF.make_hdf5_files(os.path.join(self.home_dir,self.input_zip_dir))
        
        from plot_snow_on_map import plotSnow #needs to reload this here (possible unit test bug?)
        plotHDF = plotSnow(self.data_dir,self.lat_long_area_filename,self.lat_long_coords)
        plotHDF.set_up_grid()
        

        plotHDF.make_plots_from_HDFStore(self.output_dir, show = False, save = True)

        num_plots = glob.glob(os.path.join(self.output_dir,'plots', '*.png'))
        self.assertEqual(len(num_plots), 5, 'should be 5 plots')

if __name__ == '__main__':
    unittest.main()
