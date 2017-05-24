# -*- coding: utf-8 -*-
"""
Created on Mon May 22 16:06:42 2017

@author: tyler
"""

import h5py
import os
import numpy as np
import pdb

home_dir = os.getcwd()
input_data_dir = os.path.join(home_dir, os.pardir, 'zip_files', '24km_test')
output_dir = os.path.join(os.getcwd(), os.pardir, 'output', '24km_partial')


file_names = os.listdir(output_dir)
grid_size = 1024

h5 = h5py.File(os.path.join(output_dir,os.pardir,'combined.hdf5'), "w")

h5.create_dataset("date", (0,),maxshape=(None,),dtype="S10", fillvalue="")
h5.create_dataset("corrupted",(0,),maxshape=(None,), dtype=bool, fillvalue=False)
h5.create_dataset("zipped_format",(0,),maxshape=(None,), dtype=bool, fillvalue=True)
h5.create_dataset("snow_data", (grid_size, grid_size,0),maxshape=(grid_size, grid_size,None), dtype='i8',compression="gzip", compression_opts=9)

#pdb.set_trace()
for path, dirs, files in os.walk(output_dir):
    for f in files:
        
        
        with h5py.File(os.path.join(output_dir,f), "r") as fh5:       
            #check if all keys have been added
            
            for key in fh5.keys():
            
                grp = fh5[key]
                
                for dset_name in grp.keys():
                    
                    if dset_name == 'snow_data':
                        print('snow_data')
                        dset = grp[dset_name]
                        h5_dset = h5[dset_name]
                        current_size = h5_dset.shape[-1]
                        additional_size = dset.shape[-1]
                        new_size = current_size+additional_size
                        h5_dset.resize((grid_size,grid_size,new_size))
                        h5_dset[:,:,current_size:] = dset.value #takes awhile...
    
                    else:
                        
                        try:
                            dset = grp[dset_name]
                            
                            h5_dset = h5[dset_name]
                            current_size = h5_dset.shape[0]
                            additional_size = dset.shape[0]
                            new_size = current_size+additional_size
                            h5_dset.resize((new_size,))
                            h5_dset[current_size:] = dset.value
                        except:
                            print('somthing went wrong')
                            pass
                
corrupted = h5['corrupted'].value      
date = h5['date'].value
zipped_format = h5['zipped_format'].value               
h5.close()
        