# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 09:28:07 2016

@author: tyler
"""

# mongo1.py
import h5py
from region_parameters import get_test_tibet_24x24_param
import pymongo as mongo

import numpy as np

import os
import logging
reload(logging)
import pdb

class make_database:
    
    def __init__(self, grid_size, db_name, areas_collection):
        
        logging.debug('initializing make_database')
        self.init_database(db_name)
        self.grid_size = grid_size
        self.areas_collection = areas_collection
        index_array  = np.mgrid[0:self.grid_size, 0:self.grid_size].swapaxes(0,2).swapaxes(0,1)
        self.indicies = index_array.reshape((self.grid_size)*(self.grid_size),2) 
        
    def init_database(self,db_name):
        logging.debug('initializing init_database')
        client = mongo.MongoClient('mongodb://localhost:27017/')
        # create database
        self.db = client[db_name]

    def add_area_collection(self, areas_hdf5_name):
        logging.debug('initializing add_area_collection')
        #open hdf5
        fh5 = h5py.File(areas_hdf5_name, "r")
        
        #create collection and created index
        collection = self.db[areas_collection]
        collection.create_index([('lat',mongo.DESCENDING),('long',mongo.DESCENDING)])
        
        #loop over indicies and add area document if index lies on earth.
        for idx, index in enumerate(self.indicies):
            row, col = index[0], index[1]
            area = fh5['areas'][row, col]
            
            if not area == 0.0:
                row, col = index[0], index[1]
                lat = fh5['lat'][row, col]
                lon = fh5['lon'][row, col]
                lat_centroid = fh5['lat_centroid'][row, col]
                lon_centroid = fh5['lon_centroid'][row, col]
                x_centroid = fh5['x_centroid'][row, col]
                y_centroid = fh5['y_centroid'][row, col]
                
                area_record = {
                "row": int(row),
                "col": int(col),
                "lat": float(lat),
                "lon": float(lon),
                "id_num": int(idx),
                "area":float(area),
                "centroid_lat":float(lat_centroid),
                "centroid_lon":float(lon_centroid),
                "x_centroid":float(x_centroid),
                "y_centroid":float(y_centroid),
                }
                #pdb.set_trace()
                try:
                    collection.insert(area_record)
                except:
                    logging.warning('not able to add area record: {0} \n row:{1} \n col:{2}'.format(idx, row, col))
                    pass
            if row % 250 == 0 and col == self.grid_size/2:
                #pdb.set_trace()
                logging.debug('on row: {0} col: {1}'.format(row,col))
                logging.debug('flushing hdf5')
                fh5.flush()
                
    def add_timeseries_collection(self,output_dir, hdf5_name, collection_name):

        logging.debug('initializing add_timeseries_collection')
        
        logging.debug('retrieving area collection')
        try:
            area_collection = self.db[self.areas_collection]
            curser = area_collection.find()
            id_list = []
            for area_doc in curser[:]: #can only query once. need to get ID number
                id_list.append(area_doc['id_num'])
        except:
            logging.warning('not able to retrieve area collection')
    
        logging.debug('creating time series collection: {0}'.format(collection_name))
        try:
            collection = self.db[collection_name]
            collection.create_index([('lat',mongo.DESCENDING),('long',mongo.DESCENDING), ('date',mongo.DESCENDING)])
        except:
            logging.warning('not able to create time series collection')

        with h5py.File(os.path.join(output_dir,hdf5_name), "r") as fh5:
            # loop over date, row,col
            snow_dset = fh5['snow_data']
            date_dset = fh5['date']
            corrupted_dset = fh5['corrupted']
            zipped_format_dset = fh5['zipped_format']

            #loop over each day
            for idx, date in enumerate(date_dset.value):
                corrupted = corrupted_dset[idx]
                zipped_format = zipped_format_dset[idx]
                
                for id_elem in id_list: #loop over areas in database
                    pdb.set_trace()
                    if (not collection.find_one({'id_num':id_elem}) == None) and (not date == ""):
                        area_doc = area_collection.find_one({'id_num':id_elem})
    
                        row = area_doc['row']
                        col = area_doc['col']
                        snow_entry = snow_dset[row,col,idx]
                        # add entry to db
                        snow_record = {
                        "id_num": area_doc['id_num'],
                        "snow_data": snow_entry,  
                        "date": date,
                        "corrupted": bool(corrupted),
                        "zipped_format": bool(zipped_format),                    
                        }
                        
                        try:
                            collection.insert(snow_record)
                        except:
                            logging.warning('not able to add snow record to time series collection')
            
                if idx % 5 == 0:
                    #pdb.set_trace()
                    logging.debug('on date: {0}'.format(date))

                

if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,filename='make_database.log',level=logging.DEBUG)
    logging.debug('Start of log file')     
    home_dir = os.getcwd()

    data_dir = os.path.join(home_dir,'data')
    output_dict = get_test_tibet_24x24_param()
    
    output_dir = os.path.join(home_dir,os.pardir,'output')
        
    grid_size = output_dict['grid_size']
    no_snow_planet_name = output_dict['no_snow_planet_name']
    lat_long_area_filename = output_dict['lat_long_area_filename']
    lat_long_coords = output_dict['lat_long_coords']
    
    areas_hdf5_name = "24km_areas.hdf5"    
    
    #init database
    db_name = 'test-database-2'
    areas_collection = 'twenty_four_km_areas'
    collection_name = 'twenty_four_km_time_series'
    hdf5_name = 'combined.hdf5'
    
    mdb = make_database(grid_size, db_name, areas_collection)
    mdb.add_timeseries_collection(output_dir, hdf5_name, collection_name)


        

