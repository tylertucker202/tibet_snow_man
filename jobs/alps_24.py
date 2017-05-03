from region_parameters import get_alps_24x24_param
from job_functions import run_job


if __name__ == '__main__':
    
    input_dict = get_alps_24x24_param()
    make_grid = True
    make_hdf5 = False
    make_time_series_df = False
    make_plots = False
    
    run_job(input_dict, make_grid, make_hdf5, make_time_series_df, make_plots)