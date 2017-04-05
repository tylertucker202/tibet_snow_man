# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 11:05:50 2017

@author: tyler
"""
import pandas as pd
import pdb
import os
import logging
from math import sin, cos, asin, sqrt, pi, radians
reload(logging)
import numpy as np
from generate_grid_and_area import grid_and_area, get_24x24_param, get_4x4_param
import matplotlib.pyplot as plt


import seaborn as sns
from matplotlib import rc
rc('text', usetex=False)
rc('font', family='monospace', size = 20)

colors = ["windows blue", "amber", "scarlet", "faded green", "dusty purple"]
sns.set_palette(sns.xkcd_palette(colors))

class grid_error(grid_and_area):
    
    def __init__(self,lat_long_coords,data_dir, no_snow_map_name, grid_size):
        grid_and_area.__init__(self,lat_long_coords,data_dir, no_snow_map_name, grid_size)
        self.addLatLong(lat_grid_filename,lon_grid_filename)
        self.reduceLatLong()
        self.makeNoSnowMap()
        self.addAreas()
        
    def get_surrounding_centroids(self,row_id):

        tl_point = self.df[ self.df['id'] == row_id]
        col, row = tl_point.index.values[0]
        centroid_corners = self.centroids.ix[(col, row)]['area_points']
        
        phi_1 = self.centroids.ix[centroid_corners['top_left']]['centroid_lat']
        lam_1 = self.centroids.ix[centroid_corners['top_left']]['centroid_long']
        
        phi_2 = self.centroids.ix[centroid_corners['top_right']]['centroid_lat']
        lam_2 = self.centroids.ix[centroid_corners['top_right']]['centroid_long']
        
        phi_3 = self.centroids.ix[centroid_corners['bottom_right']]['centroid_lat']
        lam_3 = self.centroids.ix[centroid_corners['bottom_right']]['centroid_long']

        phi_4 = self.centroids.ix[centroid_corners['bottom_left']]['centroid_lat']
        lam_4 = self.centroids.ix[centroid_corners['bottom_left']]['centroid_long']        
        
        return ((phi_1,lam_1),(phi_2,lam_2),(phi_3,lam_3),(phi_4,lam_4))
        
    def get_spherical_triangle(self,coords):       
        triangle_areas = []
        for i,coord in enumerate(coords):
            #print(i)
            #print((i+1)%4)
            start_coord = map(radians,coord)
            end_coord = map(radians,coords[(i+1)%4])
            phi_1, phi_2 = start_coord[0], end_coord[0]
            dist = self.haversine_formula(start_coord,end_coord)
            semi_p = self.semi_perimeter(dist, phi_1, phi_2)
            area = self.lhuilier(semi_p, dist, phi_1, phi_2)

            sign = 1 - 2*(i/2)       
            
            triangle_areas.append(area*sign)
        #pdb.set_trace()
        area = sum(triangle_areas)
        #print('area for {0}: {1}'.format(row_id, area))
        return area
    
    def spherical_polygon(self, coords):
        angles = []
        
        for i,coord in enumerate(coords):
            #print(i)
            #print((i+1)%4)
            start_coord = coord
            end_coord = coords[(i+1)%4]
            phi_1, phi_2 = start_coord[0], end_coord[0]
            dist = self.haversine_formula(start_coord,end_coord)   
            angles.append(dist)
        
        area = (sum(angles) - (len(coords) -2) * np.pi) * 6371**2
        pdb.set_trace()
        return area
    
    def haversine_formula(self,start_coord,end_coord):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # haversine formula 
        phi_1, lam_1 = start_coord
        phi_2, lam_2 = end_coord
        dlam = lam_2 - lam_1 
        dphi = phi_2 - phi_1 
        a_dist = sin(dphi/2)**2 + cos(phi_1) * cos(phi_2) * sin(dlam/2)**2
        dist = 2 * asin(sqrt(a_dist)) 
        return dist

    def semi_perimeter(self,dist, phi_1, phi_2):
        s = (dist  + pi  + (phi_1 + phi_2) )* .5
        return s
    
    def lhuilier(self,semi_p, dist, phi_1, phi_2): #uses unit sphere R=1
    
        inner_sq = np.sqrt( np.tan( 0.5*semi_p ) * 
                            np.tan( 0.5*(semi_p-dist) ) * 
                            np.tan( 0.5*(semi_p-(np.pi/2 + phi_1)) ) * 
                            np.tan( 0.5*(semi_p-(np.pi/2 + phi_2)) ) )
        Delta = 4.0 * np.arctan(inner_sq)
        
        area = 6371**2 * (Delta) #radius of earth is set at 6371 km 
        return area
        
    def get_cell_area(self,tri_top, tri_bot):
        area = tri_top - tri_bot
        return area
    
    def add_cell_area(self):
        
        
        def get_area(id_num):
            coord = self.get_surrounding_centroids(id_num)
            sp_area = self.get_spherical_triangle(coord)
            return sp_area
        
        self.df['sp_area'] = map(lambda x: get_area(x), self.df['id'])
        self.df['area_error'] = 100* (self.df['area'] - self.df['sp_area']) / self.df['sp_area']
    #def compare_cell_area():
    
    def plot_dist(self):
        fig = plt.figure(0)
        axes = plt.axes()
        axes.hist(self.df['area_error'].values, 50)
        axes.set_title('histogram of error')
        axes.set_ylabel(r'frequency')
        axes.set_xlabel(r'% error')
        plt.show()

    
if __name__ == '__main__':
    home_dir = os.getcwd()
    
    #data_dir = os.path.join(os.path.join(home_dir,os.sep,os.pardir), 'data')
    data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))
    grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename = get_24x24_param()
    #grid_size, no_snow_planet_name, lat_grid_filename, lon_grid_filename, lat_long_area_filename = get_4x4_param()

    lat_long_coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    
    #initialize object
    ge = grid_error(lat_long_coords,data_dir,no_snow_planet_name,grid_size)
    coords_0 = ge.get_surrounding_centroids(0)
    
    #add spherical triangle areas to dataframe
    ge.add_cell_area()
    
    #plot errors
    ge.plot_dist()

#    error = 100* (ge.df['area'] - ge.df['sp_area']) / ge.df['sp_area'])
#    
#
#    bottom_phi = 25 
#    top_phi = 45 
#    left_lambda = 65 
#    right_lambda = 105 
#    bottom_phi, top_phi, left_lambda, right_lambda = map(radians, [bottom_phi, top_phi, left_lambda, right_lambda])
#    test_coords = ((top_phi, left_lambda),(top_phi,right_lambda),(bottom_phi, right_lambda),(bottom_phi,left_lambda))
#    
#    #test_area = ge.spherical_polygon(test_coords)
#    test_area_0 = ge.get_spherical_triangle(coords_0)
#    test_area2 = ge.get_spherical_triangle(test_coords)
#    
#    

