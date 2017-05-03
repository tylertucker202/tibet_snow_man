#!/bin/bash

#task spooler command tsp adds a process to a queue
PYTHONPATH="${PYTHONPATH}:/home/tyler/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/"
PYTHONPATH="${PYTHONPATH}:/home/tyler/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/jobs/"

export PYTHONPATH

tsp -S 3 #sets the number of parallel jobs to 3
source activate tibet_env

#####
#QUEUE
#####
tsp python test_tibet_24.py
tsp python tibet_24.py
tsp python alberta_24.py
tsp python alps_24.py
tsp python artic_24.py
tsp python sierras_24.py

#####
#NO QUEUE
#####
#python test_tibet_24.py
#python tibet_24.py
#python alberta_24.py
#python alps_24.py
#python artic_24.py
#python sierras_24.py


