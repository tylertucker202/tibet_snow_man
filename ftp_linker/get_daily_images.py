# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 11:08:04 2017

@author: tyler
"""
import matplotlib
import pdb
import ftplib
import datetime
from urlparse import urlparse
import logging
import os
import sys
import gzip
import pylab as plt
import pandas as pd
from scipy.interpolate import griddata
import numpy as np
sys.path.append(os.path.join(os.getcwd(), os.pardir))
import region_parameters
from snowCode import makeSnowHDFStore
from plot_snow_on_map import plotSnow
matplotlib.use('Agg') # needed to run via crontab


class plotSnowCSV(plotSnow):
    """
    Plot a single csv file
    """
    def __init__(self,
                 data_dir,
                 lat_long_area_filename,
                 lat_long_coords):
        plotSnow.__init__(self,
                          data_dir,
                          lat_long_area_filename,
                          lat_long_coords)

    def make_plot_from_CSV(self,
                           filename,
                           resolution,
                           series_name,
                           image_path,
                           show=True,
                           save=False):
        my_series = pd.Series.from_csv(series_name)
        date = series_name.split('series_')[1].replace('_', '-')
        title_name = filename + '-' + date
        m = self.make_map('merc')  # Mercator projection
        data = my_series.apply(self.snow_and_ice)
        grid_z0 = griddata(self.points,
                           data.values,
                           (self.grid_x, self.grid_y),
                           method='linear')
        grid_z0[grid_z0 != 1] = np.nan  # Removes non snow elements
        # puts contour over map
        m.contourf(self.grid_x,
                   self.grid_y,
                   grid_z0,
                   latlon=False,
                   cmap=self.cmap1,
                   alpha=1)
        plt.title(title_name, fontsize=16, color="black")
        if show:
            plt.show()
        if save:
            plt.savefig(os.path.join(image_path, resolution+'.png'))
            plt.close()


class makeSnowCSV(makeSnowHDFStore):
    """
    create a single time series object and save it as a csv.
    """
    def __init__(self,
                 data_dir,
                 output_dir,
                 zip_dir,
                 lat_long_filename,
                 lat_long_coords,
                 resolution):
        self.resolution = resolution
        makeSnowHDFStore.__init__(self,
                                  data_dir,
                                  output_dir,
                                  zip_dir,
                                  lat_long_filename,
                                  lat_long_coords)

    def createTimeSeriesCSV(self, filename):
        logging.debug('inside createTimeSeriesCSV:')
        logging.debug('reading file: {}'.format(filename))
        colName = filename.split('_', 1)[0].replace('ims', '')
        colName = colName[0: 4]+'_'+colName[4:]
        dt = datetime.datetime.strptime(colName, '%Y_%j')
        series_name = self.resolution+'_'+dt.strftime('series_%Y_%m_%d')

        with gzip.open(filename, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            nominally_formatted_bool, body = self.check_if_nominally_formatted(lines, filename)

            if nominally_formatted_bool:
                try:
                    data = self.parse_normally_formatted_file(body, filename)
                    s = pd.Series(data)
                    s.to_csv(series_name)
                    logging.debug('created series for normally '
                                  'formatted filename: {}'.format(filename))
                except:
                    logging.warning('cant distinguish data '
                                    'for normally formatted filename: {}.'
                                    'Not added'.format(filename))
                    pass
            elif not nominally_formatted_bool:
                try:
                    data = self.parse_alternatively_formatted_file(body,
                                                                   filename)
                    s = pd.Series(data)
                    s.to_csv(series_name)
                    logging.debug('created series for '
                                  'alternatively formatted '
                                  'filename: {}'.format(filename))
                except:
                    logging.warning('cant distinguish data for '
                                    'alternatively formatted '
                                    'filename: {}. Not added'.format(filename))
                    pass

            if 4 not in data:
                logging.warning('no snow reported for '
                                'filename: {}'.format(filename))
        return series_name


def get_daily_folder(resolution_folder):
    today = datetime.datetime.now()
    url = urlparse('ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
    IMS_path = 'DATASETS/NOAA/G02156/'
    year_folder = today.strftime('%Y')
    PREFIX = 'ims'
    postfix = '_' + resolution_folder + '_v1.3.asc.gz'
    yesterday = today - datetime.timedelta(1)
    day_filename = yesterday.strftime(PREFIX+'%Y%j'+postfix)
    yesterday_filename =  yesterday.strftime(PREFIX+'%Y%j'+postfix)
    ftp = ftplib.FTP(url.netloc)    # connect to host, default port
    ftp.login()                     # user anonymous, passwd anonymous@
    ftp.cwd(IMS_path)               # change into "debian" directory
    ftp.cwd(resolution_folder)
    ftp.cwd(year_folder)
    files = []
    try:
        files = ftp.nlst()
    except ftplib.error_perm, resp:
        if str(resp) == "550 No files found":
            logging.warning("No files in this directory")
        else:
            raise

    if day_filename not in files:
        logging.debug('Day not posted yet. Exiting script')
        sys.exit()
    try:
        with open(day_filename, 'w') as fobj:
            ftp.retrbinary("RETR " + day_filename, fobj.write)
    except:
        logging.warning('Error in writing file: {}'.format(day_filename))
        logging.warning('Error in writing file: {}'.format(day_filename))
        ftp.quit()
    return day_filename


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='get_daily.log',
                        level=logging.INFO)
    HOME_DIR = os.getcwd()
    OUTPUT_DIR = HOME_DIR
    DATA_DIR = os.path.join(os.getcwd(), os.pardir, 'data')
    CONTENT_PATH = HOME_DIR
    INPUT_ZIP_DIR = HOME_DIR
    OUTPUT_LISTS = [region_parameters.get_tibet_24x24_param(),
                    region_parameters.get_tibet_4x4_param()]
    logging.info('starting get_daily_images.py script \n')
    for output_dict in OUTPUT_LISTS:
        lat_long_area_filename = output_dict['lat_long_area_filename']
        grid_size = output_dict['grid_size']
        lat_long_coords = output_dict['lat_long_coords']
        filename = output_dict['filename']
        ftp_filename = output_dict['ftp_filename']
        logging.info('getting daily image '
                     'for: {} resolution'.format(ftp_filename))
        logging.info('Retrieving today\'s data')
        today_filename = get_daily_folder(ftp_filename)
        logging.info('Creating today\'s csv')
        makeCSV = makeSnowCSV(DATA_DIR,
                              OUTPUT_DIR,
                              INPUT_ZIP_DIR,
                              lat_long_area_filename,
                              lat_long_coords,
                              ftp_filename)
        series_name = makeCSV.createTimeSeriesCSV(today_filename)
        logging.info('Start of plotting section')
        plotHDF = plotSnowCSV(DATA_DIR,
                              lat_long_area_filename,
                              lat_long_coords)
        plotHDF.make_plot_from_CSV(filename,
                                   ftp_filename,
                                   series_name,
                                   CONTENT_PATH,
                                   show=False,
                                   save=True)
        #  Cleanup, comment out if you want to keep images
        os.remove(series_name)
        os.remove(today_filename)
        logging.info('done with get_daily_images.py script')
