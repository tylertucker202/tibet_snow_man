#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 10:34:30 2017

@author: gstudent4
"""
import os
import logging
reload(logging)

import sys
sys.path.append(os.path.join(os.getcwd(), os.pardir))
import h5py
from makeSnowHdf5 import makeSnowHdf5


if __name__ == '__main__':
    
    
    input_data = '24km'
    home_dir = os.getcwd()
    input_data_dir = os.path.join(home_dir,os.pardir,os.pardir,'zip_files', input_data)
    output_dir = os.path.join(home_dir,os.pardir, os.pardir, 'output','24km')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    grid_size = 1024
    
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,filename=os.path.join(output_dir,'make_snow_hdf5_'+input_data+'.log'),level=logging.DEBUG)
    logging.debug('Start of log file')   
    

    logging.debug('init object')
    snw_hdf5 = makeSnowHdf5(input_data_dir,output_dir,grid_size)
    logging.debug('Parse series')
    snw_hdf5.parse_timeseries()
    
    ###to be used for testing
    file_name = input_data+'.hdf5'
    fh5 = h5py.File(os.path.join(output_dir,file_name), "r")
    
    #check if all keys have been added
    fh5.keys()
    
    #check if 2013-242 is corrupted
    fh5['2013'].keys()
    fh5['2013']['corrupted'][0] #should be false
    fh5['2013']['corrupted'][242-1] # should be true
    
    #check if 1997 is in zipped format
    fh5['1997']['zipped_format'][127-1] #should be false
    fh5['1997']['zipped_format'][35-1] #should be true
    fh5['1997']['zipped_format'][36-1] #should be true
    
    #check if dates were placed in the right order