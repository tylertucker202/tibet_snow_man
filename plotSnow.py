# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 14:23:26 2017

@author: tyler
"""
import os

import urlparse
import pandas as pd
from mpl_toolkits.basemap import Basemap
from region_parameters import get_test_tibet_24x24_param
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap
import pdb
from ftplib import FTP, error_perm
import logging
from makeMongoDatabase import makeMongoDatabase
from datetime import datetime, timedelta

class plotSnow(makeMongoDatabase):
    def __init__(self, DB_NAME,
                 RESOLUTION,
                 GRID_SIZE,
                 AREAS_COLLECTION_NAME,
                 TIME_SERIES_COLLECTION_NAME,
                 lat_lon_coords,
                 OUTPUT_DIR):
        self.RESOLUTION = RESOLUTION
        makeMongoDatabase.__init__(self,
                                   GRID_SIZE,
                                   DB_NAME,
                                   AREAS_COLLECTION_NAME)

        self.lat_lon_coords = lat_lon_coords
        self.set_up_grid()
        self.PREFIX = 'date:'
        self.OUTPUT_DIR = OUTPUT_DIR
        self.ts_df = pd.DataFrame(columns=['date', 'area', 'perc'])

    def make_map(self, proj='merc'):
        plt.cla()
        coords = self.lat_lon_coords
        center = ((coords['upper_lon'] - coords['lower_lon']) / 2 +
                  coords['lower_lon'],
                  (coords['upper_lat'] - coords['lower_lat']) / 2 +
                  coords['lower_lat'])

        if proj == 'ortho':
            """Due to a document error,
            you have to set m in terms of llcrnrx, llcrnry, etc.
            """
            m = Basemap(projection=proj,
                        resolution='c',
                        lat_0=center[1],
                        lon_0=center[0])

        elif proj == 'geos':
            # lat_0 at_0 must be zero
            m = Basemap(projection=proj,
                        llcrnrlat=coords['lower_lat'],
                        urcrnrlat=coords['upper_lat'],
                        llcrnrlon=coords['lower_lon'],
                        urcrnrlon=coords['upper_lon'],
                        lat_ts=20,
                        resolution='c',
                        lat_0=0,
                        lon_0=center[0])
        else:
            m = Basemap(epsg=3395,
                        llcrnrlat=coords['lower_lat'],
                        urcrnrlat=coords['upper_lat'],
                        llcrnrlon=coords['lower_lon'],
                        urcrnrlon=coords['upper_lon'],
                        lat_ts=20,
                        resolution='h',
                        lat_0=center[1],
                        lon_0=center[0])

        #  m.etopo()
        #  serv = 'World_Physical_Map'
        #  serv = 'World_Imagery'
        #  serv = 'World_Street_Map'
        serv = 'ESRI_StreetMap_World_2D'
        xpixl = 500
        m.arcgisimage(service=serv, xpixels=xpixl, verbose=False, zorder=0)
        #  m.bluemarble()
        #  m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='#ddaa66', lake_color='#0000ff', zorder=1)
        m.drawrivers(color='#0000ff', zorder=2)
        parallels = np.arange(0., 81, 2)
        meridians = np.arange(10, 351, 2)
        m.drawparallels(parallels, labels=[False, True, True, False])
        m.drawmeridians(meridians, labels=[True, False, False, True])
        return m

    def set_up_grid(self):
        logging.debug('inside set_up_grid')
        snow = '#FEFEFE'
        # get lat-lon points that fall in region of interest
        cursor = self.areas_collection.find(
                            {"lat":
                             {"$gte": self.lat_lon_coords['lower_lat'],
                              "$lte": self.lat_lon_coords['upper_lat']},
                             'lon':
                             {'$gte': self.lat_lon_coords['lower_lon'],
                              '$lte': self.lat_lon_coords['upper_lon']}})
        areas = []
        id_nums = []
        lat = []
        lon = []
        land_sea = []
        #pdb.set_trace()
        for doc in cursor:
            areas.append((doc['area']))
            id_nums.append(doc['id_num'])
            lat.append(doc['lat'])
            lon.append(doc['lon'])
            land_sea.append(doc['land_sea_value'])
        m = self.make_map(proj='merc')
        x, y = m(lon, lat)
        self.id_nums = id_nums
        self.df = pd.DataFrame(columns=['_id',
                                        'area',
                                        'lat',
                                        'lon',
                                        'x',
                                        'y', 'land_sea'])
        self.df['_id'] = id_nums
        self.df['lat'] = lat
        self.df['lon'] = lon
        self.df['x'] = x
        self.df['y'] = y
        self.df['areas'] = areas
        self.region_area = np.sum(areas)
        logging.debug('total area of region: {}'.format(self.region_area))
        self.df['land_sea'] = land_sea
        self.grid_x, self.grid_y = np.mgrid[min(x): max(x): 3000j,
                                            min(y): max(y): 3000j]
        self.cmap1 = LinearSegmentedColormap.from_list("my_colormap",
                                                       (snow, snow),
                                                       N=6, gamma=1)
        self.xy_points = np.transpose(np.array([x, y]))


    @staticmethod
    def snow_and_ice(_id, snow_ice_id):
        if (_id in snow_ice_id):
            x = 1
        else:
            x = 0
        return x

    def make_plots_from_collections(self,
                                    YEARS,
                                    SHOW=True,
                                    SAVE=False):
        """Makes plots from existing collections in database"""
        plt.ioff()
        names = self.db.collection_names()
        day_coll_names = filter(lambda name: self.PREFIX in name, names)
        for year in YEARS:
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year), 12, 31)
            date_range = pd.date_range(start_date, end_date)
            date_range = map(lambda date: date.strftime('%Y-%m-%d'), date_range)
            for coll_name in day_coll_names:
                start_time = datetime.now()
                date_str = coll_name.strip(self.PREFIX)
                if date_str not in date_range:
                    continue
                contour_values = self.make_contour_values(date_str, coll_name)
                if SHOW or SAVE:
                    self.make_plot_from_contour_values(date_str,
                                                       contour_values, SHOW, SAVE)
    
                self.append_coverage(date_str, contour_values)
                end_time = datetime.now()
                dt = end_time - start_time
                logging.debug('finished making plot and coverage: it took '
                              '{} seconds'.format(dt.seconds))
            self.ts_df.to_csv('mongo-ts-'+year+'.csv')
                              

    def add_timeseries_from_ftp(self, YEARS, SHOW, SAVE):
        """
        Makes plots from FTP site. Grabs file, adds it to DB,
        generate plot and coverage, and then deletes collection."""
        msg = ('inside add_timeseries_from_ftp '
               'for resolution: {}').format(self.RESOLUTION)
        logging.debug(msg)
        url = urlparse.urlparse(
                        'ftp://sidads.colorado.edu/pub/DATASETS/NOAA/G02156/')
        IMS_path = 'DATASETS/NOAA/G02156/'
        # connect to ftp and loop through years
        ftp = FTP(url.netloc)    # connect to host, default port
        ftp.login()                     # user anonymous, passwd anonymous@
        ftp.cwd(IMS_path)
        ftp.cwd(self.RESOLUTION)

        year_files = []

        def make_dir_list(ftp):
            try:
                files = ftp.nlst()
            except error_perm, resp:
                if str(resp) == '550 No files found':
                    logging.warning("""no files inside \
                                     ftp directory: {}""".format(ftp.pwd()))
                else:
                    raise
            return files

        year_files = make_dir_list(ftp)
        year_files.remove('.')
        year_files.remove('..')
        def get_date(day):
            date = day.split('_', 1)[0].replace('ims', '')
            date = date[0:4]+'_'+date[4:]
            dt = datetime.strptime(date, '%Y_%j')
            date_string = dt.strftime('%Y-%m-%d')
            return date_string

        # add each day to ts collection
        for year in year_files:
            start_time = datetime.now()
            if year not in YEARS:
                continue
            logging.debug('adding year to collection: {}'.format(year))
            ftp.cwd(year)
            days = make_dir_list(ftp)
            days.remove('.')
            days.remove('..')
            for day_filename in days:
                date_str = get_date(day_filename)
                with open(day_filename, 'w') as day_file:
                    try:
                        ftp.retrbinary('RETR ' + day_filename, day_file.write)
                        self.push_day(day_filename, date_str)
                        os.delete(day_file)
                    except:
                        logging.warning("""Error in writing file: \
                                        {}""".format(day_filename))
                        logging.warning('not going to add')
                        continue
                coll_name = self.PREFIX+date_str
                contour_values = 0
                contour_values = self.make_contour_values(date_str, coll_name)
                if SHOW or SAVE:
                    self.make_plot_from_contour_values(date_str,
                                                       contour_values,
                                                       SHOW,
                                                       SAVE)
                end_time = datetime.now()
                dt = end_time - start_time
                logging.debug('finished making plot and coverage: it took '
                              '{} seconds'.format(dt.seconds))
                logging.debug('removeing collection: {}'.format(coll_name))
                self.db.drop_collection(coll_name)

    
    def append_coverage(self, date_str, contour_values):
        """
        Calculate area covered and save to ts_df"""
        coverage = np.dot(self.df['areas'].values, contour_values.values)
        perc_coverage = 100 * coverage / self.region_area
        logging.debug('snow coverage on {0}: {1} km^2'.format(date_str, coverage))
        dic = {'area': coverage, 'date': date_str, 'perc': perc_coverage}
        self.ts_df = self.ts_df.append(dic, ignore_index=True)

    def make_contour_values(self, date_str, coll_name):

        date_coll = self.db[coll_name]
        logging.debug('Filtering for: {}'.format(date_str))
        cursor = date_coll.find({'_id': {'$in': self.id_nums}})
        if cursor is None:
            logging.warning('Did not find anything: {}'.format(date_str))
            logging.warning('continuing on, but the map will be bare')
        snow_ice_id = []
        for doc in cursor:
            snow_ice_id.append(doc['_id'])

        def contour_fun(row): return self.snow_and_ice(row['_id'], snow_ice_id)
        contour_values = self.df.apply(contour_fun, axis=1)
        return contour_values

    def make_plot_from_contour_values(self, date_str, contour_values, SHOW, SAVE):
        logging.debug('inside make_plot_from_contour_values')
        xy = self.df[['x', 'y']].values
        # create interpolated grid using array
        grid_z0 = griddata(xy,
                           contour_values,
                           (self.grid_x, self.grid_y),
                           method='linear')
        # values != 1 are set to np.nan
        grid_z0[grid_z0 != 1] = np.nan
        # make map and create contourf
        m = self.make_map('merc')
        m.contourf(self.grid_x,
                   self.grid_y,
                   grid_z0,
                   latlon=False,
                   cmap=self.cmap1,
                   zorder=3,
                   alpha=1)
        plt.title(date_str, fontsize=16, color="black")
        # show and save
        if SHOW:
            plt.show()
        if SAVE:
            plot_dir = os.path.join(OUTPUT_DIR, 'plots')
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)
            plt.savefig(os.path.join(plot_dir, date_str + '.png'))
            plt.close()


if __name__ == '__main__':
    reload(logging)  # spyder sometimes needs logging to reload.
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename='plotSnow.log',
                        level=logging.DEBUG)
    logging.debug('\nStart of log file')
    home_dir = os.getcwd()
    GRID_SIZE = 1024
    OUTPUT_DICT = get_test_tibet_24x24_param()

    OUTPUT_DIR = os.path.join(home_dir, os.pardir, 'output', OUTPUT_DICT['filename'])
    LAT_LON_COORDS = OUTPUT_DICT['lat_lon_coords']
    YEARS = map(lambda x: str(x), range(1997, 2006))

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # init database
    DB_NAME = 'twenty_four'
    AREAS_COLLECTION_NAME = 'twenty_four_km_areas'
    TIME_SERIES_COLLECTION_NAME = 'combined_dates'
    RESOLUTION = '24km'

    plotter = plotSnow(DB_NAME,
                       RESOLUTION,
                       GRID_SIZE,
                       AREAS_COLLECTION_NAME,
                       TIME_SERIES_COLLECTION_NAME,
                       LAT_LON_COORDS,
                       OUTPUT_DIR)
    #plotter.add_timeseries_from_ftp(YEARS, SHOW=False, SAVE=False)
    plotter.make_plots_from_collections(YEARS, SHOW=False, SAVE=False)
    
