#!/bin/bash
export HOME
. $HOME/.profile
. $HOME/.bashrc
PYTHONPATH="${PYTHONPATH}:/home/tibet_snow_man-master"
DAILY_SCRIPT_PATH="/home/tibet_snow_man-master/ftp_linker"
export PYTHONPATH
export DAILY_SCRIPT_PATH
cd $DAILY_SCRIPT_PATH
echo 'starting daily parser'
date
#create daily images
echo 'getting daily images'
python get_daily_images.py





