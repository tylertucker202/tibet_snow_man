# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 19:40:22 2016

@author: tyler
"""
import pandas as pd
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pdb
from scipy.interpolate import griddata
import re

#%%
#make multiindex tuples
index = []
for col in range(0, 1024):
    for row in range(0,1024):
        index.append((col,row))
df_index = pd.MultiIndex.from_tuples(index, names = ['col','row'])
#%%
#create dataframe
df = pd.DataFrame(columns = ['lat', 'long'], index = df_index)

#get lat long arrays
path = '/home/tyler/Desktop/MATH636/tibet_snowpack/snowCode_V3/'
lat_filename = 'imslat_24km.bin'
long_filename = 'imslon_24km.bin'                                 
no_snow_filename = 'dry_planet.asc'

with open(path+lat_filename, "r") as f:
    lat_array = np.fromfile(f, dtype=np.float32)               
    #list starts at bottom left corner. need to rearrange
    lat_l = lat_array.tolist()                
    lat_chunks = [lat_l[x:x+1024] for x in xrange(0, len(lat_l), 1024)]
    lat_flat = [item for sublist in lat_chunks[::-1] for item in sublist[::-1]]
    df['lat'] = lat_flat
with open(path+long_filename, "r") as f:
    long_array = np.fromfile(f, dtype=np.float32)
    long_l = long_array.tolist()               
    long_chunks = [long_l[x:x+1024] for x in xrange(0, len(long_l), 1024)]
    long_flat = [item for sublist in long_chunks[::-1] for item in sublist[::-1]]
    df['long'] = long_flat
#%%
with open(path+no_snow_filename, "r") as f:
    content = f.read()
    lines = content.split('\n')
    
    threashold = 75
    for i, line in enumerate(lines[0:100]): 
        if re.search('0{30,}', line):
            print('data found at index: {}'.format(i))
            header = lines[0:i-1]
            body = lines[i:-1]
            break                    
            break
        if i > threashold:
            print('cant distinguish header for filename: {}'.format(filename))
            break
    int_body = body #prevents altering the recursion
    for i, line in enumerate(body):
        
        line = line.replace('3','1') #ice and and snow is changed to sea and land respectively
        line = line.replace('4','2')
        int_body[i] = [int(c) for c in line]

    no_snow_matrix = np.matrix(int_body)
    no_snow_matrix = np.fliplr(no_snow_matrix)
#%%  
def rbg_convert(x):
    
    snow = (5,5,5)            
    terra = (0,128,0)
    sea = (0,0,139)
    ice = (24,25,26)
    firmament = (0,0,0)            
    
    if x == 0:
        return firmament
    elif x == 1:
        return sea
    elif x == 2:
        return terra
    elif x == 3:
        return ice
    elif x == 4:
        return snow
    else:
        print('no earth feature identified for point: {}'.format(x))
        return(x, 0, 0)
            
rbg_no_snow_matrix = map(rbg_convert, no_snow_matrix.flat)
no_snow_matrix = np.array(rbg_no_snow_matrix,dtype='uint16').reshape((1024,1024))
#%%
coords = {'lower_lat':25,'upper_lat':45,'lower_long':65,'upper_long':105} #set as lower and upper bounds for lat and long
df = df[ df['lat'] >= coords['lower_lat'] ]
df = df[ df['lat'] <= coords['upper_lat'] ]
df = df[ df['long'] >= coords['lower_long'] ]
df = df[ df['long'] <= coords['upper_long'] ]
lat_long_indexes = df.index.tolist() 

#%% Figure1
#zoom-in-area
zoom = (600,900,200,600)
backdrop = no_snow_matrix[zoom[0]:zoom[1],zoom[2]:zoom[3]]
#plot of points of interest
llm = np.matrix(lat_long_indexes)
llm_x = llm[:,1] - zoom[2]
llm_y = (llm[:,0]-zoom[0])

#take a slice at the middle (of whole file), and plot differences
#mid_point = (zoom[3]-zoom[2])/2
mid_point = 512-zoom[2]

# Two subplots, the axes array is 1-d
fig1 = plt.figure(1, figsize = (8,5))

label_fontsize = 12
ax1 = fig1.add_subplot(121)
ax2 = fig1.add_subplot(122)
plt.setp(ax1.get_xticklabels(), rotation='vertical',fontsize=12)
plt.setp(ax1.get_yticklabels(), fontsize=12)
plt.setp(ax2.get_xticklabels(), rotation='vertical',fontsize=12)
plt.setp(ax2.get_yticklabels(), fontsize=12)

#plt.figure(1, figsize=(12,5))
#ax1 = plt.subplot(1,2,1)
ax1.imshow(backdrop)
ax1.set_title('image plot of latitude file',fontsize=label_fontsize)
ax1.set_xlabel('columns',fontsize=label_fontsize)
ax1.set_ylabel('rows',fontsize=label_fontsize)


ax1.scatter(llm_x,llm_y, c='w', s=10, marker = 'o')


#zoom-in-area
#area region of interest we are going to only find areas in this region
ax1.plot([100,100],[50,250],linewidth = 2, color = 'r') #left
ax1.plot([100,350],[50,50],linewidth = 2, color = 'r') #top
ax1.plot([350,350],[50,250],linewidth = 2, color = 'r') #right
ax1.plot([100,350],[250,250],linewidth = 2, color = 'r') #bottom
ax1.plot([mid_point,mid_point],[0, (zoom[1]-zoom[0]) ], linewidth = 3, color = 'r')
ax1.annotate('mid point',fontsize=12, xy=(mid_point, 100), xycoords='data',
xytext=(.25, .75), textcoords='axes fraction',
color='r',
arrowprops=dict(arrowstyle="fancy", color='r'))

ax1.axis([0,400,300,0])

#ax2 = plt.subplot(1,2,2)
ax2.imshow(backdrop)
ax2.set_title('image plot of longitude file',fontsize=label_fontsize)
ax2.set_xlabel('columns',fontsize=label_fontsize)
ax2.set_ylabel('rows',fontsize=label_fontsize)
ax2.plot([mid_point,mid_point],[0, (zoom[1]-zoom[0]) ], linewidth = 3, color = 'r')

ax2.annotate('mid point',fontsize=12, xy=(mid_point, 100), xycoords='data',
xytext=(.25, .75), textcoords='axes fraction',
color='r',
arrowprops=dict(arrowstyle="fancy", color='r'))
ax2.scatter(llm_x,llm_y, c='w')

ax2.axis([0,400,300,0])
#area region of interest we are going to only find areas in this region
ax2.plot([100,100],[50,250],linewidth = 2, color = 'r') #left
ax2.plot([100,350],[50,50],linewidth = 2, color = 'r') #top
ax2.plot([350,350],[50,250],linewidth = 2, color = 'r') #right
ax2.plot([100,350],[250,250],linewidth = 2, color = 'r') #bottom
#%% Figure 2
lat_matrix = np.matrix(lat_chunks)
#need to flip matrix up down and left right
lat_matrix = np.fliplr(lat_matrix[::-1])
long_matrix = np.matrix(long_chunks)
#need to flip matrix up down and left right
long_matrix = np.fliplr(long_matrix[::-1])

mid_point = len(lat_chunks)/2

col_roi = range(300,550)
row_roi = range(650,850)
mid_lat = lat_matrix[650:850,mid_point]
mid_long = np.abs(long_matrix[650:850,mid_point] - long_matrix[650:850,mid_point-1]) #take horizontal distance
lat_diff = []
long_diff = []
for i in range(0, len(mid_lat)-1):
    lat_diff.append(float(np.abs(mid_lat[i+1]-mid_lat[i]))) #take vertical distance
    long_diff.append(float(mid_long[i+1]))
    
A_min = lat_diff[-1]*long_diff[-1] #min occurs at row 850
A_max = lat_diff[0]*long_diff[0] #max occurs at row 300
A_perc_diff = 100*(A_max-A_min)/A_min #approx 200% difference!
A_ratio  = A_max/A_min # A_max is approx 3.25X as large as A_min




fig2 = plt.figure(2, figsize=(10,4))
label_fontsize = 22
ax1 = fig2.add_subplot(121)
ax2 = fig2.add_subplot(122)

ax1.plot(row_roi[0:len(row_roi)-1],lat_diff)
ax1.set_title('Diff in lat along midpoint',fontsize=label_fontsize)
ax1.set_xlabel('row',fontsize=label_fontsize)
ax1.set_ylabel('differences [deg]',fontsize=label_fontsize)
ax2.plot(row_roi[0:len(row_roi)-1], long_diff)
ax2.set_title('Diff in long along midpoint',fontsize=label_fontsize)
ax2.set_xlabel('row',fontsize=label_fontsize)
ax2.set_ylabel('differences [deg]',fontsize=label_fontsize)
#plt.ylim([0, .01])
#%%
mid_points = np.zeros([lat_matrix.shape[0],lat_matrix.shape[1],2])
mid_points[:] = np.NaN

#only calculating mid point in region of interest 
for i in row_roi:    
    for j in col_roi:
        #pdb.set_trace()
        mid_points[i,j,0] = np.mean([ lat_matrix[i,j],lat_matrix[i+1,j],lat_matrix[i,j+1],lat_matrix[i+1,j+1] ])
        mid_points[i,j,1] = np.mean([ long_matrix[i,j],long_matrix[i+1,j],long_matrix[i,j+1],long_matrix[i+1,j+1] ])     
#%%
#make map
plt.figure(3)
center = ((coords['upper_long']-coords['lower_long'])/2+coords['lower_long'],(coords['upper_lat']-coords['lower_lat'])/2+coords['lower_lat'])
#m = Basemap(projection='merc',
#            llcrnrlon = coords['lower_long']-5,
#            llcrnrlat = coords['lower_lat']-5,
#            urcrnrlon = coords['upper_long']+5,
#            urcrnrlat = coords['upper_lat']+5,
#            lat_0=center[1],lon_0=center[0]
#            resolution='c')
m = Basemap(projection='laea',
            width = 4500000,
            height = 4000000,
            resolution='c',lat_0=center[1],lon_0=center[0])
#draw coastlines.
m.drawcoastlines()
# draw a boundary around the map, fill the background.
# this background will end up being the ocean color, since
# the continents will be drawn on top.
m.drawmapboundary(fill_color='None')
# fill continents, set lake color same as ocean color.
m.fillcontinents(color='None',lake_color='aqua')
#%% #calculate areas for each point. the top row and left column are left out.
area = np.zeros([lat_matrix.shape[0],lat_matrix.shape[1]])
#area[:] = np.NaN
x,y = m(mid_points[:,:,1], mid_points[:,:,0]) #given in meters

inp_x  = [x[i-1,j], x[i,j], x[i,j-1], x[i-1,j-1]]
inp_y  = [y[i-1,j], y[i,j], y[i,j-1], y[i-1,j-1]]

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))/(10**6)


for i in row_roi:    
    for j in col_roi:        
        inp_x  = [x[i-1,j], x[i,j], x[i,j-1], x[i-1,j-1]]
        inp_y  = [y[i-1,j], y[i,j], y[i,j-1], y[i-1,j-1]]
        area[i,j] = PolyArea(inp_x,inp_y)
area_roi = area[min(row_roi):max(row_roi),min(col_roi):max(col_roi)]
np.nanmin(area_roi)
np.nanmax(area)

filtered_areas = list(map(lambda x: area[x], lat_long_indexes))

df['area'] = filtered_areas

#calculate max and min area
minval = df['area'].min()
maxval = df['area'].max()

areas_size = maxval/minval #max area is approximatly 2.28X greater than min
perc_diff = (maxval-minval)/minval
#area[683,392] = 468.9
#%%
#test
i = 683
j = 392   
 
plt.cla()
center = ((coords['upper_long']-coords['lower_long'])/2+coords['lower_long'],(coords['upper_lat']-coords['lower_lat'])/2+coords['lower_lat'])
m = Basemap(projection='laea',
            width = 500000,
            height = 500000,
            resolution='c',lat_0=mid_points[i,j,0],lon_0=mid_points[i,j,1])
x,y = m(mid_points[:,:,1], mid_points[:,:,0])
#%%

inp_x  = [x[i-1,j], x[i,j], x[i,j-1], x[i-1,j-1]]
inp_y  = [y[i-1,j], y[i,j], y[i,j-1], y[i-1,j-1]]
area_ij = PolyArea(inp_x,inp_y)
#should be 468.9064444077606
test_x = [0, 24000, 24000, 0]
test_y = [0, 0, 24000, 24000]
area_test = PolyArea(test_x,test_y)
#should be 576.0
dist1 = np.sqrt( (x[i-1,j] - x[i,j])**2 +  (y[i-1,j] -  y[i,j])**2 )
dist2 = np.sqrt( (x[i,j] - x[i,j-1])**2 +  (y[i,j] -  y[i,j-1])**2 )

px, py = m(long_matrix[i,j], lat_matrix[i,j])
xt, yt = m(long_matrix[i,j-1], lat_matrix[i,j-1])
xl, yl = m(long_matrix[i-1,j], lat_matrix[i-1,j])
xr, yr = m(long_matrix[i+1,j], lat_matrix[i+1,j])
xb, yb = m(long_matrix[i,j+1], lat_matrix[i,j+1])

pt_dist = np.sqrt( (px - xt)**2 +  (py -  yt)**2 )
pr_dist = np.sqrt( (px - xr)**2 +  (py -  yr)**2 )

#%%
plt.figure(3)

m.plot(px,py, latlon = False, marker='o',color ='white')
plt.annotate('point i,k', xy=(px, py), xycoords='data',
xytext=(0, -30), textcoords='offset points',
color='r',
arrowprops=dict(arrowstyle="fancy", color='g')
)


#m.plot(xt,yt, latlon = False, marker='o',color ='white')
#plt.annotate('top', xy=(xt, yt), xycoords='data',
#xytext=(0, 30), textcoords='offset points',
#color='r',
#arrowprops=dict(arrowstyle="fancy", color='b')
#)
#
#
#m.plot(xl,yl, latlon = False, marker='o',color ='white')
#plt.annotate('left', xy=(xl, yl), xycoords='data',
#xytext=(0, 30), textcoords='offset points',
#color='r',
#arrowprops=dict(arrowstyle="fancy", color='b')
#)
#m.plot(xr,yr, latlon = False, marker='o',color ='white')
#plt.annotate('right', xy=(xr, yr), xycoords='data',
#xytext=(0, 30), textcoords='offset points',
#color='r',
#arrowprops=dict(arrowstyle="fancy", color='b')
#)
#m.plot(xb,yb, latlon = False, marker='o',color ='white')
#plt.annotate('bottom', xy=(xb, yb), xycoords='data',
#xytext=(0, 30), textcoords='offset points',
#color='r',
#arrowprops=dict(arrowstyle="fancy", color='b')
#)

m.plot(x[i-1,j],y[i-1,j], latlon = False, marker='o') 
plt.annotate('corner i-1,j', xy=(x[i-1,j], y[i-1,j]), xycoords='data',
xytext=(0, 30), textcoords='offset points',
color='r',
arrowprops=dict(arrowstyle="fancy", color='g')
)

m.plot(x[i,j],y[i,j], latlon = False, marker='o') 
plt.annotate('corner i,j', xy=(x[i,j], y[i,j]), xycoords='data',
xytext=(30, 30), textcoords='offset points',
color='r',
arrowprops=dict(arrowstyle="fancy", color='g')
)

m.plot(x[i,j-1],y[i,j-1], latlon = False, marker='o')
plt.annotate('corner i,j-1', xy=(x[i,j-1], y[i,j-1]), xycoords='data',
xytext=(-90, 15), textcoords='offset points',
color='r',
arrowprops=dict(arrowstyle="fancy", color='g')
) 
m.plot(x[i-1,j-1],y[i-1,j-1], latlon = False, marker='o') 
plt.annotate('corner i-1,j-1', xy=(x[i-1,j-1], y[i-1,j-1]), xycoords='data',
xytext=(-90, 15), textcoords='offset points',
color='r',
arrowprops=dict(arrowstyle="fancy", color='g')
)

#plot area line
m.plot([x[i-1,j], x[i,j], x[i,j-1], x[i-1,j-1],x[i-1,j]], [y[i-1,j], y[i,j], y[i,j-1], y[i-1,j-1],y[i-1,j]], latlon = False,color ='black')



#%%
#plot lat/long coordinates on a scatter plot
m.scatter(df['long'].values, df['lat'].values, latlon=True)