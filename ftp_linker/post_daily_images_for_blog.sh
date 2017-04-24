#!/bin/bash


. /home/tyler/.profile

HOME="/home/tyler"

export HOME

PYTHONPATH="${PYTHONPATH}:/home/tyler/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/"
PYTHONPATH="${PYTHONPATH}:/home/tyler/Desktop/tibet_snowpack/itsonlyamodel/"

DAILY_SCRIPT_PATH="/home/tyler/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/ftp_linker"
BLOG_PATH="/home/tyler/Desktop/tibet_snowpack/itsonlyamodel/"

export PYTHONPATH
export DAILY_SCRIPT_PATH
export BLOG_PATH

cd $DAILY_SCRIPT_PATH

#activate tibet_env so that you can run get_daily_images.py
echo 'setting tibet_env'
#source activate tibet_env

#create daily images
echo 'getting daily images'
/home/tyler/anaconda2/envs/tibet_env/bin/python get_daily_images_for_blog.py

#activate jupyter-blog enviornment so that you may operate via fab
echo 'updating blog'
#source activate jupyter-blog
#build output folder
cd $BLOG_PATH
#/home/tyler/anaconda2/envs/jupyter-blog/bin/python -c 'from fabfile import github; github()'
git checkout origin/master -- images/4km.png
git checkout origin/master -- images/24km.png
git commit -m 'testing checkout method'
git push --force origin gh-pages:master



