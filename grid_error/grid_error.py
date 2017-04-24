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
from region_parameters import get_alps_24x24_param
from generate_grid_and_area import grid_and_area
import matplotlib.pyplot as plt


import seaborn as sns
from matplotlib import rc
rc('text', usetex=False)
rc('font', family='monospace', size = 20)

colors = ["windows blue", "amber", "scarlet", "faded green", "dusty purple"]
sns.set_palette(sns.xkcd_palette(colors))

class grid_error(grid_and_area):
    
    def __init__(self,lat_long_coords,data_dir, no_snow_map_name, grid_size, plot_name):
        grid_and_area.__init__(self,lat_long_coords,data_dir, no_snow_map_name, grid_size)
        self.addLatLong(lat_grid_filename,lon_grid_filename)
        self.reduceLatLong()
        self.makeNoSnowMap()
        self.addAreas()
        self.plot_name = plot_name
        
    def get_surrounding_centroids(self,row_id):

        tl_point = self.df[ self.df['id'] == row_id]
        col, row = tl_point.index.values[0]
        centroid_corners = self.centroids.ix[(col, row)]['area_points']
        #pdb.set_trace()
        
        phi_1 = self.centroids.ix[centroid_corners['top_left']]['centroid_lat']
        lam_1 = self.centroids.ix[centroid_corners['top_left']]['centroid_long']
        #lam_1 = lam_1 - self.centroids['centroid_long'].min()
        
        phi_2 = self.centroids.ix[centroid_corners['top_right']]['centroid_lat']
        lam_2 = self.centroids.ix[centroid_corners['top_right']]['centroid_long']
        #lam_2 = lam_2 - self.centroids['centroid_long'].min()
        
        phi_3 = self.centroids.ix[centroid_corners['bottom_right']]['centroid_lat']
        lam_3 = self.centroids.ix[centroid_corners['bottom_right']]['centroid_long']
        #lam_3 = lam_3 - self.centroids['centroid_long'].min()
        
        phi_4 = self.centroids.ix[centroid_corners['bottom_left']]['centroid_lat']
        lam_4 = self.centroids.ix[centroid_corners['bottom_left']]['centroid_long']        
        #lam_4 = lam_4 - self.centroids['centroid_long'].min()
        
        return ((phi_1,lam_1),(phi_2,lam_2),(phi_3,lam_3),(phi_4,lam_4))
        
    def get_spherical_triangle(self,coords):       
        triangle_areas = []
        
        def get_tri_area(coord):
            start_coord = map(radians,coord)
            end_coord = map(radians,coords[(i+1)%4])
            phi_1, phi_2 = start_coord[0], end_coord[0]
            dist = self.haversine_formula(start_coord,end_coord)
            semi_p = self.semi_perimeter(dist, phi_1, phi_2)
            tri_area = self.lhuilier(semi_p, dist, phi_1, phi_2)

            
            return tri_area
                
        #TODO: figure out how to determine sign of triangle
        #is minimum value always correct?
        for i,coord in enumerate(coords):
 
            tri_area= get_tri_area(coord)
            sign = 1 - 2*(i/2) 
            triangle_areas.append(tri_area*sign)
        area = sum(triangle_areas)
        if abs(area) > 1000:
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
            #sp_area = self.spherical_polygon(coord)
            return sp_area
        
        
        self.df['sp_area'] = map(lambda x: get_area(x), self.df['id'])
        self.df['area_error'] = 100* (self.df['area'] - self.df['sp_area']) / self.df['sp_area']

    
    def plot_dist(self, save = True):
        fig = plt.figure(0)
        axes = plt.axes()
        axes.hist(self.df['area_error'].values, 50)
        axes.set_title('histogram of error')
        axes.set_ylabel(r'frequency')
        axes.set_xlabel(r'% error')
        plt.show()
        if save:
            plt.savefig(self.plot_name)
    

    
if __name__ == '__main__':
    home_dir = os.getcwd()
    
    data_dir = os.path.join(os.path.join(os.getcwd(),os.pardir,os.pardir), 'data')
    #data_dir = os.path.abspath(os.path.join(os.getcwd() , os.pardir, 'data'))
  
    input_dict = get_alps_24x24_param()
    ftp_filename = input_dict['ftp_filename']
    grid_size = input_dict['grid_size']
    no_snow_planet_name = input_dict['no_snow_planet_name']
    lat_grid_filename = input_dict['lat_grid_filename']
    lon_grid_filename = input_dict['lon_grid_filename']
    lat_long_area_filename = input_dict['lat_long_area_filename']
    lat_long_coords = input_dict['lat_long_coords']
    plot_name = input_dict['filename']
    
    #initialize object
    ge = grid_error(lat_long_coords,data_dir,no_snow_planet_name,grid_size,plot_name)
    coords_0 = ge.get_surrounding_centroids(0)
    
    #add spherical triangle areas to dataframe
    ge.add_cell_area()
    #plot errors
    ge.plot_dist(save = True)
    
    
    
#outlier investigation
outliers = ge.df[abs(ge.df['area_error']) > 50]
outlier_coord = ge.get_surrounding_centroids(2019)
outlier_area = ge.get_spherical_triangle(outlier_coord)
start_coord,end_coord = [map(radians,outlier_coord[0]), map(radians,outlier_coord[(0+1)%4])]
l1 = ge.haversine_formula(start_coord,end_coord)

start_coord,end_coord = [map(radians,outlier_coord[1]), map(radians,outlier_coord[(1+1)%4])]
l2 = ge.haversine_formula(start_coord,end_coord)

start_coord,end_coord = [map(radians,outlier_coord[2]), map(radians,outlier_coord[(2+1)%4])]
l3 = ge.haversine_formula(start_coord,end_coord)

start_coord,end_coord = [map(radians,outlier_coord[3]), map(radians,outlier_coord[(3+1)%4])]
l4 = ge.haversine_formula(start_coord,end_coord)

area_outliers = (sum([l1,l2,l3,l4]) - (len([l1,l2,l3,l4]) -2) * np.pi) * 6371**2

ge.haversine_formula(start_coord,end_coord)

#normal investigation
coord = ge.get_surrounding_centroids(0)
area = ge.get_spherical_triangle(coord)
start_coord,end_coord = [map(radians,coord[0]), map(radians,coord[(0+1)%4])]
l1 = ge.haversine_formula(start_coord,end_coord)

start_coord,end_coord = [map(radians,coord[1]), map(radians,coord[(1+1)%4])]
l2 = ge.haversine_formula(start_coord,end_coord)

start_coord,end_coord = [map(radians,coord[2]), map(radians,coord[(2+1)%4])]
l3 = ge.haversine_formula(start_coord,end_coord)

start_coord,end_coord = [map(radians,coord[3]), map(radians,coord[(3+1)%4])]
l4 = ge.haversine_formula(start_coord,end_coord)

area = (sum([l1,l2,l3,l4]) - (len([l1,l2,l3,l4]) -2) * np.pi) * 6371**2
    
    
    


