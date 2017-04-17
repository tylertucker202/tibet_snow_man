# -*- coding: utf-8 -*-

from region_parameters import get_test_tibet_24x24_param
from job_functions import run_job


if __name__ == '__main__':
    
    input_dict = get_test_tibet_24x24_param()
    make_grid = True
    make_hdf5 = True
    make_time_series_df = True
    make_plots = True
    
    run_job(input_dict, make_grid, make_hdf5, make_time_series_df, make_plots)
   