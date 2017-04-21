#!/bin/bash

PYTHONPATH="${PYTHONPATH}:$HOME/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/"

#PYTHONPATH="${PYTHONPATH}:$HOME/Desktop/tibet_snowpack/itsonlyamodel/"

DAILY_SCRIPT_PATH="$HOME/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/ftp_linker"
BLOG_PATH="$HOME/Desktop/tibet_snowpack/itsonlyamodel"

export PYTHONPATH
export DAILY_SCRIPT_PATH
export BLOG_PATH

cd $DAILY_SCRIPT_PATH

#activate tibet_env so that you can run get_daily_images.py
source activate tibet_env

#create daily images
python get_daily_images_for_blog.py

#activate jupyter-blog enviornment so that you may operate via fab
source activate jupyter-blog
#build output folder
cd $BLOG_PATH
fab build
#upload to github
fab github
