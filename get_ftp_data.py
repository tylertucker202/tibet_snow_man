#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:04:55 2017

@author: gstudent4
"""

from ftplib import FTP

import urlparse
import logging
import os
import numpy as np
reload(logging) #need to reload in spyder
import re
import pdb

def get_yearly_dataset(resolution_folder, year_folder):


    url = urlparse.urlparse('ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
    IMS_path = 'DATASETS/NOAA/G02156/'

    
    ftp = FTP(url.netloc)    # connect to host, default port
    ftp.login()                     # user anonymous, passwd anonymous@
    ftp.cwd(IMS_path)               # change into "debian" directory
    #ftp.retrlines('LIST')           # list directory contents
    ftp.cwd(resolution_folder)
    ftp.cwd(year_folder)
    
    
    all_files = ftp.nlst() #get all files
    my_regex = re.compile(".*.asc.gz")
    to_download = filter(my_regex.match, all_files) #find .asc.gz files
    
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)
        
    os.chdir(year_folder) #bad style, but fobj.write won't put the files in year_folder
    
    for asc_file in to_download:
        try:
            with open(asc_file, 'w') as fobj:
                ftp.retrbinary("RETR " + asc_file ,fobj.write)
        except:
            print "Error"
            
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    ftp.quit()
    
if __name__ == '__main__':   
    
    twenty_four_dir = '24km'
    four_dir = '4km'
    one_dir = '1km'
    
    twenty_four_km_years = map(lambda x: str(x), np.arange(1997,2018,1))
    four_km_years = map(lambda x: str(x), np.arange(2004,2018,1))
    one_km_years = map(lambda x: str(x), np.arange(2011,2018,1))
    
    #get 24 km data
    for year_folder in twenty_four_km_years:
        
        if not os.path.exists(twenty_four_dir):
            os.mkdir(twenty_four_dir)
        os.chdir(twenty_four_dir)
        
        get_yearly_dataset(twenty_four_dir, year_folder)