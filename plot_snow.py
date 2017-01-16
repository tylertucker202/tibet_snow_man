# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 18:55:53 2016

@author: tyler
"""
import os
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from matplotlib.colors import LinearSegmentedColormap
import datetime
from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
### for Palatino and other serif fonts use:
##rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=False)



import pdb
#make map
#%%
def makeMap(proj='merc'):
    plt.cla()
    coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
    center = ((coords['upper_long']-coords['lower_long'])/2+coords['lower_long'],(coords['upper_lat']-coords['lower_lat'])/2+coords['lower_lat'])
    
    if proj == 'ortho':
        #Due to a document error, you have to set m in terms of llcrnrx, llcrnry, etc.
        m = Basemap(projection=proj,
                    resolution='c', 
                    lat_0 = center[1],
                    lon_0 = center[0])
        #pdb.set_trace()
        #llcrnrx, llcrnry = m(coords['lower_lat'],coords['lower_long'])
        #urcrnrx, urcrnry = m(coords['upper_lat'],coords['upper_long'])

        #m = Basemap(projection=proj,
        #llcrnrx=llcrnrx,
        #llcrnry=llcrnry,
        #urcrnrx=urcrnrx,
        #urcrnry=urcrnry,
        #resolution='c', 
        #lat_0 = center[1],
        #lon_0 = center[0])    
    elif proj == 'geos':
        #lat_0 must be zero
        m = Basemap(projection=proj,
            llcrnrlat=coords['lower_lat'],
            urcrnrlat=coords['upper_lat'],
            llcrnrlon=coords['lower_long'],
            urcrnrlon=coords['upper_long'],
            lat_ts=20,
            resolution='c', 
            lat_0 = 0,
            lon_0 = center[0])        
    else:
        m = Basemap(projection=proj,
            llcrnrlat=coords['lower_lat'],
            urcrnrlat=coords['upper_lat'],
            llcrnrlon=coords['lower_long'],
            urcrnrlon=coords['upper_long'],
            lat_ts=20,
            resolution='c', 
            lat_0 = center[1],
            lon_0 = center[0])
        
    
    #m.drawcoastlines()
    # draw a boundary around the map, fill the background.
    # this background will end up being the ocean color, since
    # the continents will be drawn on top.
    #m.drawmapboundary(fill_color='None')
    # fill continents, set lake color same as ocean color.
    #m.fillcontinents(color='None',lake_color='aqua')
    #m.bluemarble()                   
    #m.shadedrelief()
    m.etopo()
    parallels = np.arange(0., 81, 10)
    meridians = np.arange(10, 351, 10)
    m.drawparallels(parallels, labels =[False, True, True, False])
    m.drawmeridians(meridians, labels =[True, False, False, True])
    return m
#%%
    
fig = plt.figure()
# global ortho map centered on lon_0,lat_0
lat_0=10.; lon_0=57.
# resolution = None means don't process the boundary datasets.
m1 = Basemap(projection='ortho',lon_0=lon_0,lat_0=lat_0,resolution=None)
# add an axes with a black background
ax = fig.add_axes([0.1,0.1,0.8,0.8],axisbg='k')
# plot just upper right quadrant (corners determined from global map).
# keywords llcrnrx,llcrnry,urcrnrx,urcrnry used to define the lower
# left and upper right corners in map projection coordinates.
# llcrnrlat,llcrnrlon,ucrnrlon,urcrnrlat could be used to define
# lat/lon values of corners - but this won't work in cases such as this
# where one of the corners does not lie on the earth.
m = Basemap(projection='ortho',lon_0=lon_0,lat_0=lat_0,resolution='l',\
    llcrnrx=0.,llcrnry=0.,urcrnrx=m1.urcrnrx/2.,urcrnry=m1.urcrnry/2.)
m.drawcoastlines()
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='coral',lake_color='aqua')
m.drawcountries()
# draw parallels and meridians.
m.drawparallels(np.arange(-90.,120.,30.))
m.drawmeridians(np.arange(0.,360.,60.))
m.drawmapboundary()
plt.title('Orthographic Map Showing A Quadrant of the Globe')
plt.show()
#%%
#Needs work:
#Lambert Azimuthal Equal Area Projection: laea
#must specify lat_0 and long_0
plt.figure(0)
m_laea= makeMap('laea')    
#Mercator Projection: merc
plt.figure(1)
m_merc= makeMap('merc') 
#Azimuthal Equidistant Projection
plt.figure(2)
m_aeqd=makeMap('aeqd') 
#Gnomic projection
plt.figure(3)
m_aeqd = makeMap('gnom')
#Needs work, make a global option?:
#Orthographic projection
plt.figure(4)
m_orth = makeMap('ortho')

#Geostationary projection
plt.figure(5)
m_geos = makeMap('geos')

#Equidistant Cylindrical Projection
plt.figure(6)
m_cyl = makeMap('cyl')

#Cassini
plt.figure(7)
m_cass = makeMap('cass')

#Transverse Mercator Projection
plt.figure(8)
m_tmerc = makeMap('tmerc')

#Polyconic Projection
plt.figure(9)
m_poly = makeMap('poly')

#Gall Stereographic Projection
plt.figure(10)
m_gall = makeMap('gall')

#Miller Cylindrical Projection
plt.figure(11)
m_mill = makeMap('mill')

#Lambert Conformal Projection
plt.figure(12)
m_lcc = makeMap('lcc')

#Stereographic Projection
plt.figure(13)
m_stere = makeMap('stere')

#Equidistant Conic Projection
plt.figure(14)
m_eqdc = makeMap('eqdc')

#Albers Equal Area Projection
plt.figure(15)
m_aea = makeMap('aea')
#%%
def snow_and_ice(x):
    if x==4 or x==3:
        x=1 
    else: 
        x=0
    return x

snow = '#FEFEFE'            
terra = '#00ff7f'
sea = '#007fff'
ice = '#A5F2F3'
firmament = '#26211f'



#%%
def make_plot_from_col(df, col, plot_dir, show = True, save = False):
    year, day = df[col].name.split("_")
    date = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(day))
    title_string = date.strftime('%Y-%m-%d')
    m=makeMap('merc')
    data = df[col].apply(snow_and_ice)
    grid_z0 = griddata(points, data.values, (grid_x, grid_y), method='linear') #can be nearest, linear, or cubic interpolation
    grid_z0[ grid_z0 != 1 ] = np.nan
    m.contourf(grid_x, grid_y,grid_z0, latlon=False, cmap = cmap1, alpha=1)
    plt.title(title_string,fontsize=16, color = "black")
    if show:
        plt.show()
    if save:
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        plt.savefig(plot_dir+col+'.png')
        plt.close()

#%%
#Setup grid

os.chdir('/home/tyler/Desktop/tibet_snowpack/Tibet Project/snowCode/')

direc = '/home/tyler/Desktop/tibet_snowpack/Tibet Project/snowCode/data/'

df_lat_long = pd.read_csv(direc+'lat_long_centroids_area_24km.csv')
lat = df_lat_long['lat'].values
lon = df_lat_long['long'].values
m=makeMap()
x,y = m(lon,lat)
points = np.transpose(np.array([x,y]))
grid_x, grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]
cmap1 = LinearSegmentedColormap.from_list("my_colormap", (snow, snow), N=6, gamma=1)
plt.close()
points = np.transpose(np.array([x,y]))
grid_x, grid_y = np.mgrid[min(x):max(x):3000j, min(y):max(y):3000j]


#%%
csv_to_plot_dir = 'output/24km_test/'
filename = '1997.csv'
plot_dir = csv_to_plot_dir+'plots_fun/'
df = pd.read_csv(csv_to_plot_dir+filename)

#make_plot_from_col(df, df.columns[1], plot_dir, show = True, save = False) #TEST


plt.ioff()
for col in df.columns[1:]:
    make_plot_from_col(df, col, plot_dir, show = False, save = True)

#%%
#run thru loop without function

plt.ioff()

csv_to_plot_dir = 'output/24km_test/'
filename = '1997.csv'
output_dir = os.getcwd()+'/output/'


for col in df.columns[1:]:
    year, day = df[col].name.split("_")
    date = datetime.datetime(int(year), 1, 1) + datetime.timedelta(int(day))
    title_string = date.strftime('%Y-%m-%d')  

    m=makeMap()
    data = df[col].apply(snow_and_ice)
    grid_z0 = griddata(points, data.values, (grid_x, grid_y), method='linear') #can be nearest, linear, or cubic interpolation
    grid_z0[ grid_z0 != 1 ] = np.nan
    m.contourf(grid_x, grid_y,grid_z0, latlon=False, cmap = cmap1, alpha=1)
    plt.title(title_string,fontsize=16, color = "black")
    plt.savefig('output/24km_test/plots/'+col+'.png')
    #pdb.set_trace()
    plt.close()
    
