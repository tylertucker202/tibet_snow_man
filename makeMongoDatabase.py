# -*- coding: utf-8 -*-
import h5py
import pymongo as mongo
import numpy as np
import os
import logging
import pdb
from datetime import datetime, timedelta
from ftplib import FTP, error_perm
from urllib.parse import urlparse
#import urlparse
import socket
import gzip
from itertools import islice, chain


class makeMongoDatabase(object):

    def __init__(self,
                 GRID_SIZE,
                 DB_NAME,
                 AREAS_COLLECTION_NAME):

        logging.debug('initializing make_database')
        self.GRID_SIZE = GRID_SIZE
        self.AREAS_COLLECTION_NAME = AREAS_COLLECTION_NAME
        self.init_database(DB_NAME)
        self.parsing_times = []

    def init_database(self, DB_NAME):
        logging.debug('initializing init_database')
        client = mongo.MongoClient('mongodb://localhost:27017/')
        # create database
        self.db = client[DB_NAME]
        self.areas_collection = self.db[self.AREAS_COLLECTION_NAME]

    def init_day_collection(self, day_coll_name):
        logging.debug('Creating new collection: {}'.format(day_coll_name))
        try:
            day_collection = self.db[day_coll_name]
            # keeps values unique
            if day_collection.count() == 0:
                day_collection.create_index(
                            [('_id', mongo.ASCENDING),
                             ('date', mongo.ASCENDING)], unique=True)
        except:
            logging.warning('not able to get time series collection')
        return day_collection

    def add_area_collection(self, AREAS_HDF5):
        logging.debug('initializing add_area_collection')
        # open hdf5
        fh5 = h5py.File(AREAS_HDF5, 'r')
        if self.areas_collection.count() == 0:
            self.areas_collection.create_index([('lat', mongo.DESCENDING),
                                                ('long', mongo.DESCENDING)])
        area_dset = fh5.get('areas')
        lat_dset = fh5.get('lat')
        lon_dset = fh5.get('lon')
        lat_centroid_dset = fh5.get('lat_centroid')
        lon_centroid_dset = fh5.get('lon_centroid')
        x_centroid_dset = fh5.get('x_centroid')
        y_centroid_dset = fh5.get('y_centroid')
        land_sea_dset = fh5.get('land_sea_values')
        records = []
        for row in range(0, self.GRID_SIZE):
            area_row = area_dset[row, :]
            lat_row = lat_dset[row, :]
            lon_row = lon_dset[row, :]
            lat_centroid_row = lat_centroid_dset[row, :]
            lon_centroid_row = lon_centroid_dset[row, :]
            x_centroid_row = x_centroid_dset[row, :]
            y_centroid_row = y_centroid_dset[row, :]
            land_sea_row = land_sea_dset[row, :]
            for col in range(0, self.GRID_SIZE):
                if area_row[col] == 0.0 or np.isnan(area_row[col]):
                    continue
                area = area_row[col]
                lat = lat_row[col]
                lon = lon_row[col]
                lat_centroid = lat_centroid_row[col]
                lon_centroid = lon_centroid_row[col]
                x_centroid = x_centroid_row[col]
                y_centroid = y_centroid_row[col]
                land_sea_value = land_sea_row[col]
                id_num = self.GRID_SIZE * row + col
                if land_sea_value == 0:
                    continue
                area_record = {
                                'row': int(row),
                                'col': int(col),
                                'lat': float(lat),
                                'lon': float(lon),
                                'id_num': int(id_num),
                                'area': float(area),
                                'centroid_lat': float(lat_centroid),
                                'centroid_lon': float(lon_centroid),
                                'x_centroid': float(x_centroid),
                                'y_centroid': float(y_centroid),
                                'land_sea_value': int(land_sea_value),
                                'dates': []
                               }
                records.append(area_record)
                if len(records) > 10000:  # faster to add many at once
                    try:
                        self.areas_collection.insert_many(records)
                        records = []
                    except:
                        pdb.set_trace()
                        logging.warning('not able to '
                                        'add area records')
            if row % 250 == 0:
                logging.debug('on row: {0}'.format(row))

        rec_length = len(records)
        if rec_length == 1:
            self.areas_collection.insert(records[0])
        elif rec_length > 1:
            try:
                self.areas_collection.insert_many(records)
            except:
                pdb.set_trace()
                logging.warning('not able to '
                                'add area record: '
                                '{0} \n row:{1} \n'
                                'col:{2}'.format(id_num, row, col))
                pass

            if row % 250 == 0 and col == self.GRID_SIZE/2:
                logging.debug('on row: {0} col: {1}'.format(row, col))
                logging.debug('flushing hdf5')
                fh5.flush()

    @staticmethod
    def get_daily_folder(resolution_folder):

        today = datetime.now()
        url = urlparse.urlparse(
            'ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
        IMS_path = 'DATASETS/NOAA/G02156/'

        year_folder = today.strftime('%Y')

        prefix = 'ims'
        postfix = '_'+resolution_folder+'_v1.3.asc.gz'
        yesterday = today - timedelta(1)
        day_filename = yesterday.strftime(prefix+'%Y%j'+postfix)

        ftp = FTP(url.netloc)    # connect to host, default port
        ftp.login()                     # user anonymous, passwd anonymous@
        ftp.cwd(IMS_path)               # change into 'debian' directory
        # ftp.retrlines('LIST')           # list directory contents
        ftp.cwd(resolution_folder)
        ftp.cwd(year_folder)

        try:
            with open(day_filename, 'w') as fobj:
                ftp.retrbinary('RETR ' + day_filename, fobj.write)
        except:
            print('Error in writing file: {}'.format(day_filename))
        ftp.quit()
        return day_filename

    def push_today(self, resolution, zip_dir):
        logging.debug('inside push_today')
        # get today's file
        today_zip_file_name = self.get_daily_folder(resolution)
        today = datetime.today()
        today_date = today.strftime('%Y-%m-%d')
        try:
            self.push_day(today_zip_file_name, today_date)
        except:
            logging.warning('Error in writing file: {}'.format(today_date))
            logging.warning('not going to add')
            pass
        os.remove(today_zip_file_name)

    def push_dates(self, RESOLUTION_FOLDER, YEARS):
        msg = ('inside push_dates '
               'for resolution: {}').format(RESOLUTION_FOLDER)
        logging.debug(msg)
        url = urlparse.urlparse(
                        'ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
        IMS_path = 'DATASETS/NOAA/G02156/'
        # connect to ftp and loop through years
        ftp = FTP(url.netloc)    # connect to host, default port
        ftp.login()                     # user anonymous, passwd anonymous@
        ftp.cwd(IMS_path)
        ftp.cwd(RESOLUTION_FOLDER)

        year_files = []

        def make_dir_list(ftp):
            try:
                files = ftp.nlst()
            except error_perm:
                raise
            return files

        year_files = make_dir_list(ftp)

        def get_date(day):
            date = day.split('_', 1)[0].replace('ims', '')
            date = date[0: 4] + '_' + date[4:]
            dt = datetime.strptime(date, '%Y_%j')
            date_string = dt.strftime('%Y-%m-%d')
            return date_string

        # add each day to ts collection
        for year in year_files[2:]:
            if year not in YEARS:
                continue
            logging.debug('adding year to collection: {}'.format(year))
            ftp.cwd(year)
            days = make_dir_list(ftp)

            for day_filename in days[2:]:
                start_time = datetime.now()
                try:
                    date_string = get_date(day_filename)
                except:
                    logging.warning('unable to add: {}'.format(day_filename))
                    continue
                with open(day_filename, 'w') as day_file:
                    try:
                        ftp.retrbinary('RETR ' + day_filename, day_file.write)
                    except socket.error as err:
                        logging.warning('Socket error when writing file: '
                                        '{}'.format(err))
                try:
                    self.push_day(day_filename, date_string)
                except:
                    logging.warning('Error in writing file: '
                                    '{}'.format(day_filename))
                    logging.warning('not going to add')
                    pass
                os.remove(day_filename)
                end_time = datetime.now()
                dt = end_time - start_time
                self.parsing_times.append(dt.seconds)
                logging.debug('Finshed adding day:{0}\nTime it took '
                              'to parsethrough date:'
                              '{1}'.format(date_string, dt.seconds))
            #  go up a dir and continue to the next year.
            ftp.cwd("../")


    def push_day(self, day_file_name, date_string):
        '''
        Assumes day_file_name contains header on lines 0-29,
        and data is nxn, starting on line 30.
        '''
        logging.debug('inside push_day '
                      'for day: {}'.format(date_string))
        self.day_collection = self.init_day_collection(self.PREFIX+date_string)
        if (not self.day_collection.find_one() == None):
            logging.warning('date: {} already in db. '
                            'Possible duplicates. '
                            'Not going to add'.format(date_string))
            return

        # loop over rows and add each one to the database
        start_line = 30
        with gzip.open(day_file_name, 'r') as f:
            """
            files are set in two formats, zipped and unzipped
            """
            pilot_row = next(islice(f, 30, 30+1))

        with gzip.open(day_file_name, 'r') as f:
            if ' ' in pilot_row:
                logging.debug('Uncompressed file '
                              'for date: {0}'.format(date_string))
                # uncompressed files are added using a separate function.
                try:
                    self.push_uncompressed_day(f, date_string)
                except:
                    logging.warning('not able to add uncompressed '
                                    'file: {}'.format(date_string))
                    pass
            for row, line in enumerate(islice(f, start_line, None)):
                try:
                    # sometimes there is a newline
                    line = line.strip('\n')
                    # remove land/sea to save space
                    line = line.replace('1', '0')
                    line = line.replace('2', '0')
                    snow_line = map(lambda x: int(x), line)
                    snow_array = np.array(snow_line)
                    non_zero_elements = np.where(snow_array != 0)
                except IOError as err:
                    logging.warning('problem occured when creating int_body')
                    logging.warning('error: {0}'.format(err))
                if row % 1000 == 0:
                    logging.debug('on row: {0}'.format(row))
                if non_zero_elements[0].size == 0:
                    continue
                try:
                    self.push_snow_array(snow_array, row, date_string)
                except IOError as err:
                    logging.warning('not able to add compressed '
                                    'file: {}'.format(date_string))
                    pass
                except ValueError as err:
                    logging.warning('problem occured when creating int_body')
                    logging.warning('error: {0}'.format(err))
                    pass

        '''
        This checks if there is any snow.
        Sometimes a file wont have any snow or ice values'''
        if self.day_collection.find_one() == None:
            logging.warning('no snow or ice displayed setting as corrupt')
            logging.warning('filename: {}'.format(date_string))
            self.dates.insert({'corrupted_date': date_string})

    def push_uncompressed_day(self, day_file, date_string):
        int_body = []
        start_line = 22
        for idx, line in enumerate(islice(day_file, start_line, None)):
            try:
                line = line.replace(' ', '')
                line = line.strip('\n')
                line = line.replace('164', '3')
                line = line.replace('165', '4')
                int_body.append([int(c) for c in line])
            except ValueError as err:
                logging.warning('problem occured when creating int_body')
                logging.warning('error: {0}'.format(err))
                pass
            except IOError as err:
                logging.warning('problem occured when creating int_body')
                logging.warning('error: {0}'.format(err))
        try:
            flat_body = list(chain.from_iterable(int_body))
            body_m = np.array(flat_body)
            body_m = body_m.reshape(1024, 1024)  # only occurs in 24km grid
        except ValueError as err:
            logging.warning('Value Error:{}'.format(err))
            logging.warning('not able to format uncompressed file')
        for row, snow_array in enumerate(body_m):
            if row % 1000 == 0:
                logging.debug('on row: {0}'.format(row))
            non_zero_elements = np.where(snow_array != 0)
            if non_zero_elements[0].size == 0:
                continue
            self.push_snow_array(snow_array, row, date_string)

    def push_snow_array(self, snow_array, row, date_string):
        records = []
        for col, snow_entry in enumerate(snow_array):
            if snow_entry < 3:  # only snow and ice are added
                continue
            id_num = int(row * self.GRID_SIZE + col)
            snow_record = {
                   '_id': id_num
                  }
            records.append(snow_record)

            if len(records) >= 10000:  # keeps records small
                logging.debug('on row:{0}, inserting records'.format(row))
                try:
                    self.day_collection.insert_many(records)
                    records = []
                except:
                    logging.warning('not able to add row: {0} '
                                    'of to day collection'.format(row))
                    pass
        try:
            if len(records) == 1:
                self.day_collection.insert_one(records[0])
            elif len(records) > 1:
                self.day_collection.insert_many(records)
        except mongo.errors.WriteError as err:
            pdb.set_trace()
            logging.warning('Write Error: {}'.format(err))
            logging.warning('system ulimit may have to be extended')
            logging.warning('not able to add row: {0} '
                            'of date {1} snow record to '
                            'day collection'.format(row, date_string))
            pass