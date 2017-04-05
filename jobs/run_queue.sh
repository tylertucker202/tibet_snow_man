#!/bin/sh

#task spooler command tsp adds a process to a queue
PYTHONPATH="${PYTHONPATH}:/home/tyler/Desktop/tibet_snowpack/tibet_project/tibet_snow_man/"

export PYTHONPATH

tsp -S 3 #sets the number of parallel jobs to 3

#####
#QUEUE
#####
tsp python tibet_24.py
tsp python tibet_24.py
tsp python tibet_24.py

