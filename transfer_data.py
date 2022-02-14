import os
import numpy as np
import shutil
import json

def generate_job_list(origin_file_name, new_file_name):
    # Open origin file
    origin_array = []
    with open(origin_file_name, mode='r', encoding='utf-8') as origin_file:
        # Create array of genus list from the file
        for x in origin_file:
            origin_array.append(x.split(":")[0])

    # Array is sorted alphabetically
    origin_array.sort()

    # Create new "remainder" file
    np.savetxt(new_file_name, origin_array, fmt="%s")

    source = new_file_name
    destination = "backups/" + new_file_name.split('/')[1]
    shutil.copy(source, destination)


base_directory = 'E:/fungidata/'
destination_directory = 'E:/fungitest/'

origin_genus_file = 'metadata/genus_id_totals.txt'
unrelated_file = 'metadata/unrelated_articles.json'
job_file = 'metadata/transfer_data_job.txt'


if os.path.isfile(job_file) is False:  
    generate_job_list(origin_genus_file, job_file)

job_array = 

shutil.copy(unrelated_file, destination_directory + unrelated_file.split('/')[1])
