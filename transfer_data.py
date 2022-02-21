from email.mime import base
import os
import copy
import numpy as np
import shutil
import json

def generate_job_list(origin_file_name, new_file_name, filer_json):
    # Open origin file
    origin_array = []
    with open(origin_file_name, mode='r', encoding='utf-8') as origin_file:
        # Create array of genus list from the file
        for x in origin_file:
            item = x.split(":")[0]
            if (item != 'Total'):
                origin_array.append(item)

    # Array is sorted alphabetically
    origin_array.sort()

    # Create new "remainder" file
    np.savetxt(new_file_name, origin_array, fmt="%s")

    source = new_file_name
    destination = "backups/" + new_file_name.split('/')[1]
    shutil.copy(source, destination)


def get_array(file):
    array = []
    with open(file, mode='r', encoding='utf-8') as array_file:
        array = array_file.read().splitlines()

    return array


# Directories for base data and where to transfer
base_directory = 'E:/fungidata/'
destination_directory = 'E:/fungitest/'

# File names used for operations
origin_genus_file = 'metadata/genus_id_totals.txt'
unrelated_file = 'metadata/unrelated_articles.json'
job_file = 'metadata/transfer_data_job.txt'

# Step 1: Generate list
# if os.path.isfile(job_file) is False:  
generate_job_list(origin_genus_file, job_file, unrelated_file)

base_array = get_array(job_file)
base_array_copy = copy.deepcopy(base_array)
job_array = []
unrelated_json = []

with open(unrelated_file, 'r') as json_file:
    unrelated_json = json.load(json_file)

# Transfer for NCBI pulled articles
for item in base_array:
    print('------------------')

    if(item != 'Total'):
        print('Starting job for ' + item + ':')
        
        unrelated_ids = unrelated_json[item]
        file_directory = base_directory + item + '/'
        file_addition =  item + '/'

        ids = [file_name.split('_')[1].split('.')[0] for file_name in os.listdir(file_directory)]

        for id in ids:
            if (id != 'index' and id not in unrelated_ids):
                id_file_name = item + '_' + id + '.json'

                # Makes item directory if nonexistant
                new_item_directory = destination_directory
                dirname = os.path.dirname(new_item_directory)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                
                # Creates copies of id's based on unrelated articles
                shutil.copy(file_directory + id_file_name, new_item_directory + id_file_name)
        print('Completed!')
    else:
        print('Ignoring Total')

    # Removes item from job_file once completed
    base_array_copy.pop(0)
    with open(job_file, 'w') as f:
        f.writelines('\n'.join(base_array_copy))
    
    shutil.copy(job_file, "backups/" + job_file.split('/')[1])
