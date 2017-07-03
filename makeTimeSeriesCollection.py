# -*- coding: utf-8 -*-
from region_parameters import get_24x24_param
import pymongo as mongo
import numpy as np

import os
import logging
import pdb
from itertools import islice, chain
from map_reduce_functions import map_time_series
from map_reduce_functions import reduce_time_series
from makeMongoDatabase import makeMongoDatabase
from bson import son
from datetime import datetime
import pandas as pd


class makeTimeSeriesCollection(makeMongoDatabase):
    logging.debug('initializing makeTimeSeriesCollection')

    def __init__(self,
                 GRID_SIZE,
                 DB_NAME,
                 AREAS_COLLECTION_NAME):
        self.PREFIX = 'date:'
        makeMongoDatabase.__init__(self,
                                   GRID_SIZE,
                                   DB_NAME,
                                   AREAS_COLLECTION_NAME)

    def init_ts_collection(self,
                           EPOCH,
                           NAME='ts_array',
                           end_date='2018-01-01'):
        """
        Creates an array of zeros from the EPOCH till an end_date
        end date should be set once a year or so.
        """
        logging.debug('starting init_ts_collection')
        ts_coll = self.db[NAME]
        if self.db[NAME].find_one() != None:
            logging.debug('ts collection exists already under'
                          'name:{}'.format(NAME))
        dates = pd.date_range(EPOCH, end_date)
        empty_array = np.zeros(dates.shape).tolist()
        ts_coll = self.db[NAME]
        cursor = self.areas_collection.find()
        dates = map(lambda date: date.strftime('%Y-%m-%d'), dates)
        pdb.set_trace()
        date_record = {'_id': 0, 'dates': dates}
        try:
            ts_coll.insert(date_record)
        except mongo.errors.DuplicateKeyError as err:
            logging.warning(err)
            logging.warning('dates record already exists. not replacing.')
            pass
        for doc in cursor:
            record = {'_id': doc['id_num'],
                      'ts': empty_array}
            try:
                ts_coll.insert(record)
            except mongo.errors.DuplicateKeyError as err:
                logging.warning(err)
                logging.warning('_id {} already exists. not '
                                'replacing.'.format(doc['id_num']))
                pass
        logging.debug('finished with init_ts_collection')
        pdb.set_trace()
        return

    def set_ts_collection(self, NAME='ts_array',YEARS=[2017],DELETE_DAYS=True):
        """
        Dates collections set an existing file containing an array of booleans.
        Each element represents a day from a certain epoch.
        collection that updates that date with data.
        """
        ts_coll = self.db[NAME]
        logging.debug('Inside set_ts_collection')
        # get names
        names = self.db.collection_names()
        day_names = filter(lambda name: self.PREFIX in name, names)
        logging.debug('Number of dates: {}'.format(len(day_names)))

        dates_doc = ts_coll.find_one({'_id': 0})
        ts_coll_list = dates_doc['dates']
        dates_added = dates_doc['added']
        """
        loop over each date, updating self.ts_coll with
        that day's snow and ice data. Bypassing document validation 
        speeds up the process"""
        bypass_document_validation = True
        for day in day_names:
            start_time = datetime.now()
            logging.debug('adding collection: {}'.format(day))
            coll = self.db[day]
            cursor = coll.find()
            date = day.strip(self.PREFIX)

            #  get array of ids to add for the day
            day_ids = []
            for doc in cursor:
                day_ids.append(doc['_id'])
            pdb.set_trace()
            #  get index of array that will be updated.
            date_idx = ts_coll_list.index(date)
            ts_array_elem = 'ts.'+str(date_idx)
            try:
                #  first find if the date has been added
                if date in dates_added:
                    logging.warning('day already added. not going to update '
                                    'for day collection:{}'.format(day))
                    continue

                result = ts_coll.update_many({'_id': {'$in': day_ids}},
                                             {'$set': {ts_array_elem: 1}},
                                             bypass_document_validation)
                num_mod = result.modified_count
                if not num_mod == result.matched_count:
                    raise IOError
                logging.debug('day was added to ts_coll.')
                logging.debug('amount added: {}'.format(num_mod))
            except IOError:
                logging.warning('mongod did not update all documents for '
                                'collection: {0}'.format(day))
                logging.warning('not going to delete collection')
                continue
            except:
                logging.warning('did not update time series for '
                                'collection: {}'.format(day))
            #  add added_date to list.
            try:
                dates_added.append(date)
                ts_coll.update_one({'_id': 0},
                                   {'$set': {'added': dates_added}})
            except:
                logging.warning('failed to add date {} to added list '
                                'collection: {}'.format(date))
            # once sucessfull, remove collection from database
            if DELETE_DAYS:
                logging.debug('removing collection: {}'.format(day))
                self.db.drop_collection(day)
                end_time = datetime.now()
                dt = end_time - start_time
                logging.debug('adding day took: {} sec'.format(dt.seconds))


if __name__ == '__main__':
    reload(logging)
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='makeTimeSeriesCollection.log',
                        level=logging.DEBUG)
    logging.debug('Start of log file \n')
    HOME_DIR = os.getcwd()
    OUTPUT_DIR = os.path.join(HOME_DIR, os.pardir, 'output')
    OUTPUT_DICT = get_24x24_param()
    GRID_SIZE = OUTPUT_DICT['grid_size']
    MERGE_COLLECTION_NAME = 'fourKmTest'
    # init database
    DB_NAME = 'twenty_four'
    AREAS_COLLECTION_NAME = 'twenty_four_km_areas'
    # collection_name = 'test_twenty_four_km_time_series'
    RESOLUTION = '24km'
    #  EPOCH = '1997-02-04'
    EPOCH = '2004-02-23'
    DATA_DIR = os.path.join(HOME_DIR, os.pardir, 'data')
    AREAS_HDF5 = os.path.join(DATA_DIR, AREAS_COLLECTION_NAME+'.hdf5')
    ZIP_DIR = os.path.join(HOME_DIR, os.pardir, 'zip_files', RESOLUTION)
    YEARS = map(lambda x: str(x), range(1997, 2006))
    TIME_SERIES_COLLECTION_NAME = 'ts_array'

    if not os.path.exists(ZIP_DIR):
        logging.debug('making directory: {0}'.format(ZIP_DIR))
        os.mkdir(ZIP_DIR)

    mdb = makeTimeSeriesCollection(GRID_SIZE,
                                   DB_NAME,
                                   AREAS_COLLECTION_NAME)
    #mdb.add_area_collection(AREAS_HDF5)
    #mdb.push_today(RESOLUTION, ZIP_DIR)
    mdb.push_dates(RESOLUTION, YEARS)
    #mdb.set_ts_collection(TIME_SERIES_COLLECTION_NAME,DELETE_DAYS=False)
    #mdb.combine_dates(COMBINED_COLLECTION_NAME)
