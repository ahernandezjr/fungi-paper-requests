import os
import shutil
import numpy as np
import json
import csv
import string
import requests

# Modify all files within a directory from their genus name to guild assignment according to funguild
# @params: 'start_directory' = initial directory, 'end_directory' = destination directory for files
def rename_to_guild(start_directory, end_directory, request_url):
    genus_to_guild = {}
    no_genus_to_guild = {}
    all_files = os.listdir(start_directory)
    
    progress_bar(0, len(all_files))

    for index, file_name in enumerate(all_files):

        genus = file_name.split('_')[0]
        guild = ''

        # Get 'guild' from either genus from dictionary or retrieve it and add it to dictionary
        if (genus in genus_to_guild):
            guild = genus_to_guild[genus]
        elif (genus in no_genus_to_guild):
            shutil.copy(start_directory + file_name, end_directory + 'no_guild/' + file_name)
            
            progress_bar(index + 1, len(all_files))
            continue
        else:
            query_json = get_query_json(request_url + genus)

            # If no results, send the file into an alternate folder
            if query_json == None:
                no_genus_to_guild[genus] = [guild]

                shutil.copy(start_directory + file_name, end_directory + 'no_guild/' + file_name)
                
                progress_bar(index + 1, len(all_files))
                continue

            # If a list is returned of responses return, then iterate through them
            if(isinstance(query_json, list)):
                # Find genus from a list of genera and append to reference dictionary
                backup_guild = query_json[0]['guild']
                if ('-' not in backup_guild and backup_guild != 'NULL'):
                    guild = backup_guild

                for result in query_json:
                    if '-' not in backup_guild:
                        guild = backup_guild
                
                if guild == '':
                    guild = backup_guild

                # Append to reference dictionary 
                genus_to_guild[genus] = [guild]
            else:
                # Find genus and append to reference dictionary
                guild = query_json['guild']
                genus_to_guild[genus] = [guild]

        # Rename file based on guild name
        new_file_name = guild + '_' + file_name.split('_')[1]

        # Creates copies of id's based on unrelated articles
        shutil.copy(start_directory + file_name, end_directory + new_file_name)

        progress_bar(index + 1, len(all_files))


# Create two text files, one for genera with guilds and one for genera without guilds
# @params: 'start_directory' = initial directory, 'end_directory' = destination directory for files
def create_guilds_texts(start_directory, end_directory, request_url):
    genus_to_guild = {}
    no_genus_to_guild = {}
    all_files = os.listdir(start_directory)
    print(all_files[-1])
    
    progress_bar(0, len(all_files))

    for index, file_name in enumerate(all_files):

        genus = file_name.split('_')[0]
        guild = ''

        # Get 'guild' from either genus from dictionary or retrieve it and add it to dictionary
        if (genus in genus_to_guild):
            guild = genus_to_guild[genus]
        elif (genus in no_genus_to_guild):
            progress_bar(index + 1, len(all_files))

            continue
        else:
            query_json = get_query_json(request_url + genus)

            # If no results, send the file into an alternate folder
            if query_json == None:
                no_genus_to_guild[genus] = [guild]

                progress_bar(index + 1, len(all_files))
                continue

            # If a list is returned of responses return, then iterate through them
            if(isinstance(query_json, list)):
                # Find genus from a list of genera and append to reference dictionary
                backup_guild = query_json[0]['guild']
                if ('-' not in backup_guild and backup_guild != 'NULL'):
                    guild = backup_guild

                for result in query_json:
                    if '-' not in backup_guild:
                        guild = backup_guild
                
                if guild == '':
                    guild = backup_guild

                # Append to reference dictionary 
                genus_to_guild[genus] = [guild]
            else:
                # Find genus and append to reference dictionary
                guild = query_json['guild']
                genus_to_guild[genus] = [guild]

        progress_bar(index + 1, len(all_files))

    
    no_result_file = 'no_results_file.txt'
    with open(no_result_file, 'w') as f:
        for key in no_genus_to_guild:
            f.write(key + '\n')
    
    result_file = 'results_file.txt'
    with open(result_file, 'w') as f:
        for key in genus_to_guild:
            f.write(key + '\n')


# Convert json to csv format
def json_to_csv(start_directory, end_directory):
    progress_bar(0, len(files))

    files = [file for file in os.listdir(start_directory) if os.path.isfile(file)]

    for index, file_name in enumerate(files):
        with open(file_name, 'r') as json_file:
           text_data = json.load(json_file)["text"]

        # Format file without puncuation

        category_name = file_name.split('_')[0]
        csv_file_name = file_name.split('.')[0]

        with open(csv_file_name + '.csv', mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',',)

            csv_writer.writerow(['category', 'text'])
    
        progress_bar(index + 1, len(files))


# Gets request type and formats to json or returns None for empty json
def get_query_json(request):
    response = requests.get(request).text
    if (response == '0 results' or response == '[]'):
        return None
    return json.loads(response)

# Simple progress bar to show data
# @params: current = numerator, total = denominator
def progress_bar(current, total, bar_length = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces  = ' ' * (bar_length - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')


FUNGUILD_URL = 'https://www.mycoportal.org/funguild/services/api/db_return.php?qDB=funguild_db&qField=taxon&qText='

base_directory = 'E:/fungi_ncbi/'
transfer_directory = 'E:/fungi_ncbi_guild/'

rename_to_guild(base_directory, transfer_directory, FUNGUILD_URL)
# create_guilds_texts(base_directory, transfer_directory, FUNGUILD_URL)
