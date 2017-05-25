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
import gzip
import os
import logging
reload(logging)
import pdb
import datetime
from itertools import islice
from ftplib import FTP
import urlparse

class make_database:
    
    def __init__(self, grid_size, db_name, areas_collection_name, time_series_collection_name):

        logging.debug('initializing make_database')
        self.grid_size = grid_size
        self.areas_collection_name = areas_collection_name
        index_array  = np.mgrid[0:self.grid_size, 0:self.grid_size].swapaxes(0,2).swapaxes(0,1)
        self.indicies = index_array.reshape((self.grid_size)*(self.grid_size),2) 
        self.time_series_collection_name = time_series_collection_name
        self.init_database(db_name)
        
    def init_database(self,db_name):
        logging.debug('initializing init_database')
        client = mongo.MongoClient('mongodb://localhost:27017/')
        # create database
        self.db = client[db_name]
        self.areas_collection = self.db[self.areas_collection_name]

    def add_area_collection(self, areas_hdf5_name):
        logging.debug('initializing add_area_collection')
        #open hdf5
        fh5 = h5py.File(areas_hdf5_name, "r")
        
        self.areas_collection.create_index([('lat',mongo.DESCENDING),('long',mongo.DESCENDING)])
        
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
                    self.areas_collection.insert(area_record)
                except:
                    logging.warning('not able to add area record: {0} \n row:{1} \n col:{2}'.format(idx, row, col))
                    pass
            if row % 250 == 0 and col == self.grid_size/2:
                #pdb.set_trace()
                logging.debug('on row: {0} col: {1}'.format(row,col))
                logging.debug('flushing hdf5')
                fh5.flush()
                
    def get_daily_folder(self,resolution_folder):
    
        today = datetime.datetime.now()
        url = urlparse.urlparse('ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
        IMS_path = 'DATASETS/NOAA/G02156/'
        
        year_folder = today.strftime('%Y')
        
        prefix = 'ims'
        postfix = '_'+resolution_folder+'_v1.3.asc.gz'
        yesterday = today - datetime.timedelta(1)
        day_filename = yesterday.strftime(prefix+'%Y%j'+postfix)
        
        ftp = FTP(url.netloc)    # connect to host, default port
        ftp.login()                     # user anonymous, passwd anonymous@
        ftp.cwd(IMS_path)               # change into "debian" directory
        #ftp.retrlines('LIST')           # list directory contents
        ftp.cwd(resolution_folder)
        ftp.cwd(year_folder)
        
        try:
            with open(day_filename, 'w') as fobj:
                ftp.retrbinary("RETR " + day_filename ,fobj.write)
        except:
            print "Error in writing file: {}".format(day_filename)
        
        ftp.quit()
        return day_filename

    def add_today_to_ts_collection(self, resolution, zip_dir):
        logging.debug('inside add_today_to_ts_collection')
        logging.debug('retrieving area and time series collections')
        pdb.set_trace()
        try:
            time_series_collection = self.db[self.time_series_collection_name] 
            #keeps values unique
            time_series_collection.create_index(
                [('id_num', mongo.ASCENDING),
                 ('date', mongo.ASCENDING)],
                  unique=True)
        except:
            logging.warning('not able to get collections')
            
        #get today's file
        today_zip_file_name = self.get_daily_folder(resolution)
        today = datetime.datetime.today()
        today_date = today.strftime('%Y-%m-%d')
        
        if (not time_series_collection.find_one({'date':today_date}) == None):
            logging.warning('date: {} already in db. Possible duplicates'.format(today_date))      
        
        with gzip.open(today_zip_file_name, 'r') as f:
            
            corrupted = False
            zipped_format = True
            
            #loop over rows and add each one to the database
            start_line = 30
            for row, line in enumerate(islice(f, start_line, None)):
    
                line = line.strip('\n') #sometimes there is a newline
                line = line.replace('1','0') #remove land and sea to save space
                line = line.replace('2','0')
                snow_line = map(lambda x: int(x) ,line)  
                snow_array = np.array(snow_line)
                non_zero_elements = np.where(snow_array != 0)
                
                if non_zero_elements[0].size == 0:
                    continue
                row_of_records = [] #I figured it could be better to insert_many
                for col, snow_entry in enumerate(snow_line):
                    
                    if snow_entry == 0: #empty rows are ignored
                        continue
                    area_doc = self.areas_collection.find_one({'row':row, 'col':col})
                    
                    if area_doc == None: #areas don't exist along border, so they are removed.
                        continue
                    
                    # add entry to db
                    snow_record = {
                    "id_num": area_doc['id_num'],
                    "snow_data": snow_entry,  
                    "date": today_date,
                    "corrupted": bool(corrupted),
                    "zipped_format": bool(zipped_format),                    
                    }
                    
                    row_of_records.append(snow_record)
                    
                    if len(row_of_records) >=500: #keeps row of records small
                        print('on row: {0}. inserting row of records'.format(row))
                        time_series_collection.insert_many(row_of_records)
                        row_of_records = []
                
                if row % 250 == 0:
                    print('on row: {0}'.format(row))
                    logging.debug('on row: {0}'.format(row))
                
                try:                    
                    if not len(row_of_records)==0:
                        time_series_collection.insert_many(row_of_records)
                except:
                    logging.warning('not able to add row: {0} of today\'s snow record to time series collection'.format(row))
                    pass     
                    
        #check if there is snow 
        mid_row = time_series_collection.find_one({'row':self.grid_size/2, 'date':today_date, 'snow_data': { '$in': [3, 4] } })
        if mid_row == None:
            logging.warning('no snow or ice displayed on middle row...setting as corrupt')
            logging.warning('filename: {}'.format(today_zip_file_name))
            time_series_collection.update_many({'date':today_date}, {'corrupted':bool(True)})
                        
        
        #move file to zip_file directory 
        
        logging.debug('move {0} to zip_file directory: {1}'.format(today_zip_file_name,zip_dir))
        os.rename(today_zip_file_name, os.path.join(zip_dir,today_zip_file_name))
        logging.debug('leaving add_today_to_ts_collection')
        
                
    def add_timeseries_collection(self,output_dir, hdf5_name):

        logging.debug('initializing add_timeseries_collection')
        
        logging.debug('retrieving area collection')
        try:
            curser = self.area_collection.find()
            id_list = []
            for area_doc in curser[:]: #can only query once. need to get ID number
                id_list.append(area_doc['id_num'])
        except:
            logging.warning('not able to retrieve area collection')
    
        logging.debug('creating time series collection: {0}'.format(self.collection_name))
        try:
            time_series_collection = self.db[self.time_series_collection_name]
            time_series_collection.create_index([('lat',mongo.DESCENDING),
                                                 ('long',mongo.DESCENDING),
                                                 ('date',mongo.DESCENDING)],
                                                  unique=True)
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
                    if (not time_series_collection.find_one({'id_num':id_elem}) == None) and (not date == ""):
                        area_doc = self.area_collection.find_one({'id_num':id_elem})
    
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
                            time_series_collection.insert(snow_record)
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
    collection_name = 'test_twenty_four_km_time_series'
    hdf5_name = 'combined.hdf5'
    resolution = '24km'
    zip_dir = os.path.join(home_dir,os.pardir,'zip_files',resolution)
    
    if not os.path.exists(zip_dir):
        logging.debug('making directory: {0}'.format(zip_dir))
        os.mkdir(zip_dir)
    
    mdb = make_database(grid_size, db_name, areas_collection,collection_name)
    mdb.add_today_to_ts_collection(resolution, zip_dir)
    #mdb.add_timeseries_collection(output_dir, hdf5_name)


        

