#!/bin/sh

#task spooler command tsp adds a process to a queue
PYTHONPATH="${PYTHONPATH}:/home/gstudent4/Desktop/tibet_project/tibet_snow_man/"

export PYTHONPATH

#tsp -S 3 #sets the number of parallel jobs to 3

#####
#QUEUE
#####
#tsp python tibet_24.py
#tsp python tibet_24.py
#tsp python tibet_24.py

#####
#NO QUEUE
#####
python tibet_24.py
python alberta_24.py
python alps_24.py
python artic_24.py
python sierras_24.py


