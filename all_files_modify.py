from random import sample
import time

import os
import shutil
import numpy as np
import json
import csv
import string
import re
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
                no_genus_to_guild[genus] = guild

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
                genus_to_guild[genus] = guild
            else:
                # Find genus and append to reference dictionary
                guild = query_json['guild']
                genus_to_guild[genus] = guild

        # Rename file based on guild name
        # new_file_name = guild + '_' + file_name.split('_')[1]
        new_file_name = guild + '_' + str(index).zfill(7) + '.json'

        # Creates copies of id's based on unrelated articles
        shutil.copy(start_directory + file_name, end_directory + new_file_name)

        progress_bar(index + 1, len(all_files))
        
    # print('Files not processed: ' + str(j))
    # print('Files not processed: ' + str(i))


# Splits files with multiple guilds into each file
def csv_split(start_directory, end_directory):
    normal_files = [file for file in os.listdir(start_directory) if os.path.isfile(start_directory + file)]
    split_files = [file for file in normal_files if '-' in file]

    progress_bar(0, len(split_files))

    for index, file_name in enumerate(normal_files):

        # Perform split operation, change csv file to single category, and then copy file
        if(file_name in split_files):
            # Split
            guild_list = file_name.split('_', 1)[0].split('-')

            # Copy with new name
            for guild in guild_list:
                seperate_file_name = guild + '_' + file_name.split('_', 1)[1]

                # Change csv file 'category'
                with open(start_directory + file_name) as csv_read_file:
                    csv_lines = list(csv.reader(csv_read_file))

                for line in csv_lines[1:]:
                    line[0] = guild

                # Write/copy 'new' file
                with open(end_directory + seperate_file_name, 'w+') as csv_write_file:
                    writer = csv.writer(csv_write_file)
                    writer.writerows(csv_lines)

                # shutil.copy(start_directory + file_name, end_directory + seperate_file_name)

        # Copy file like normal
        else:
            shutil.copy(start_directory + file_name, end_directory + file_name)

        progress_bar(index + 1, len(split_files))
            

# Create two text files, one for genera with guilds and one for genera without guilds
# @params: 'start_directory' = initial directory, 'end_directory' = destination directory for files
def create_guilds_txts(start_directory, end_directory, request_url):
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
                no_genus_to_guild[genus] = guild

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
                genus_to_guild[genus] = guild
            else:
                # Find genus and append to reference dictionary
                guild = query_json['guild']
                genus_to_guild[genus] = guild

        progress_bar(index + 1, len(all_files))

    
    no_result_file = 'guild_no_results_file.txt'
    with open(no_result_file, 'w') as f:
        for key in no_genus_to_guild:
            f.write(key + '\n')
    
    result_file = 'guild_results_file.txt'
    with open(result_file, 'w') as f:
        for key in genus_to_guild:
            f.write(key + '\n')


# Convert json to csv format
def json_to_csv(json_directory, csv_directory):
    files = [file for file in os.listdir(json_directory) if os.path.isfile(json_directory + file)]
    progress_bar(0, len(files))

    for index, file_name in enumerate(files):
        # Obtain file name for csv and guild/category name
        csv_file_name = file_name.split('.')[0]
        category_name = file_name.split('_')[0]

        # Open file for 'text' data
        with open(json_directory + file_name, mode='r') as json_file:
            json_data = json.load(json_file)
            text_data = json_data["text"]
            genus_name = json_data["genus"]

        # Remove punctuation from 'text'
        # translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
        # text_data = text_data.translate(translator)

        # Remove commas from 'text' and reduce multiple punctuations to one instance
        text_data = text_data.replace(',', ' ')
        text_data = re.sub(r'(\W)(?=\1)', '', text_data)

        csv_file_name = csv_directory + csv_file_name.split('_')[0] + '_' + genus_name + '_' + csv_file_name.split('_')[1] + '.csv'

        # Open file for csv writing (and creates with 'w+' if doesn't exist)
        with open(csv_file_name, mode='w+', newline='') as csv_file:
            # Create cvs wrte object and write first row
            csv_writer = csv.writer(csv_file, delimiter=',',)
            csv_writer.writerow(['category', 'text'])

            token_list = text_data.split()
            batch_size = 200
            text_sections = []

            # Iterate through entire text [batch_size] at a time
            for i in range(0, len(token_list), batch_size):
                text_section = (' ').join(token_list[i:i+batch_size])
                # text_sections.append((' ').join(token_list[i:i+batch_size]))
                
                csv_writer.writerow([category_name, text_section])
            # csv_writer.writerows([category_name, text_sections])
    
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

genus_name_dir = 'E:/fungi_ncbi/'
transfer_dir = 'E:/fungi_ncbi_guild/'
csv_dir = 'E:/fungi_ncbi_csv_combined_guild/'
split_csv_dir = 'F:/fungi_ncbi_csv_split_guild/'

# rename_to_guild(genus_name_dir, transfer_dir, FUNGUILD_URL)
# create_guilds_txts(genus_name_dir, transfer_dir, FUNGUILD_URL)
# json_to_csv(transfer_dir, csv_dir)
csv_split(csv_dir, split_csv_dir)
