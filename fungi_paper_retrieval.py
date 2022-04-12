from posixpath import dirname
import shutil
import os
import copy
from time import sleep
from unittest import skip
import numpy as np
import re
import requests
import xml.etree.ElementTree as ET
import json

# Retrieving genus list
# WARNING: Only used the first time
# @params: data from origin file inserted into new file
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


# Create an array from a file
# @params: file = file to pull array from
def get_array(file):
    array = []
    with open(file, mode='r', encoding='utf-8') as array_file:
        array = array_file.read().splitlines()

    return array


# Create index files with ID's for all papers of a genus
# @params: query = genus-to-be-searched
def create_indicies(query_list, directory='data/'):
    # First and second parts of the url
    BASE_URL1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term='
    BASE_URL2 = '&retmax=1000000'

    # Start of looping through genus_list to get all ids
    for query in query_list:
        sleep(0.35)
        query = query.strip()

        # Make Directory if !exists
        filename = directory + query + "/"
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        search_url = query.join([BASE_URL1, BASE_URL2])
        response = True

        while True:
            response = requests.get(search_url)
            if not 'application/json' in response.headers.get('Content-Type'):
                break
            sleep(1)
        
        # Create index file for query within designated query folder
        with open(dirname + "/" + query + "_index.txt", "w") as f:
            # Response is stored into a local xml file to process and view
            with open("temp.xml", "w") as temp:
                temp.write(response.text)

            # DEBUG: Just a test file to see content-type
                # with open("test.xml", "w") as test:
                #     test.write(response.headers.get('Content-Type'))
                
            # Transforms data to be parsed by xml
            tree = ET.parse("temp.xml")
            root = tree.getroot()

            # Get id_count from xml and write to index_log for future reference
            id_count = root.find('Count').text
            print(f"Obtained {id_count} ID's for {query}")
            if (id_count.encode('utf-8') == b'0'):
                with open("metadata/index_log.log", "a+") as index_log:
                    if (f"{query}:No Results Found\n" not in index_log):
                        index_log.write(f"{query}:No Results Found\n")
                continue

            for id in root.findall('IdList/Id'):
                f.write(id.text + "\n")


# Compute total number of IDs found for data analysis
# @params: genus_list = list of the genus to view index files
def compute_total_ids(genus_array, directory='data/'):
    # Variable for sum
    total = 0

    with open('metadata/genus_id_totals.txt', 'w') as id_file:
        for genus in genus_array:
            # Gets file location of index for genus
            filename = directory + genus + '/'
            dirname = os.path.dirname(filename)

            # Gets total ID's in file and does calculations and writing to total file
            this_total = sum(1 for line in open(dirname + '/' + genus + '_index.txt'))
            total += this_total
            id_file.write(genus + ':' + str(this_total) + '\n')
        
        id_file.write('Total: ' + str(total) + '\n')
    

# Gets index of a genus from its folder/file
# @params: query_list = list of genuses (queries)) to be searched and data pulled
def get_index(query, directory='data/'):
    filename = directory + query + '/'
    dirname = os.path.dirname(filename)
    index_file_location = dirname + '/' + query + '_index.txt'

    # Takes all IDs from index of query
    with open(index_file_location) as index_file:
        index_array = index_file.read().splitlines()

    return index_array


# Get papers from a list of genuses to be searched
# @params: query = genus, index_array = list of ID's to get papers from
def create_articles_from_array(query, index_array, directory='data/'):
    x = 0
    skipped_articles = []

    # Make Directory if !exists
    filename = directory + query + "/"
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='
    url_append = ','.join(index_array)
    search_url = BASE_URL + url_append

    # Gets response 
    while True:
        response = requests.get(search_url)
        if not 'application/json' in response.headers.get('Content-Type'):
            break
        print('DELAYING REQUEST...')
        sleep(1)
    
    with open("temp_article.xml", 'w') as temp_article:
        temp_article.write(response.text)
    
    root = ET.fromstring(response.text)

    # Inner for loop for adding papers from requests
    if(len(index_array) == 1):
        # DEGUGGINS:
        # print("article: 1")

        # Determine ID with preference for PMC
        id = None
        pmc = None
        pmid = None
        doi = None
        for child in root.findall('.//front/article-meta/article-id'):
            id = sanitize_text(child.text)
            if(child.get('pub-id-type') == 'pmc'):
                pmc = sanitize_text(child.text)
            elif(child.get('pub-id-type') == 'pmid'):
                pmid = sanitize_text(child.text)
            elif(child.get('pub-id-type') == 'doi'):
                doi = sanitize_text(child.text)
        if(pmc): id = pmc
        elif(pmid): id = pmid
        elif(doi): id = doi

        # Stops inputting if article
        # Checks if the article is pullable or not
        if(root.find('.//body')):
            # Converting body to proper format
            body = sanitize_text(ET.tostring(root.find('.//body'), encoding='utf-8', method='text').decode('utf-8'))
            text = body

            if(root.find('.//front/article-meta/abstract')):
                abstract = sanitize_text(ET.tostring(root.find('.//front/article-meta/abstract'), encoding='utf-8', method='text').decode('utf-8'))
                text = abstract + ' ' + body

            # Json Array that holds the title, id, and text
            query_array = {
                "id": id,
                "genus": query,
                "text": text
            }

            # Creating file
            with open(dirname + '/' + query + '_' + id + '.json', 'w', encoding='utf-8') as f:
                json.dump(query_array, f, indent=3)
        else:  
            skipped_articles.append(id)
            
    else:
        for article in root.findall('article'):
            with open("temp_article.xml", 'w') as temp_article:
                temp_article.write(sanitize_text(ET.tostring(article, encoding='utf-8', method='text').decode('utf-8')))

            # DEBUGGING:
            # x += 1
            # print("article: " + str(x))

            # Determine ID with preference for PMC
            id = None
            pmc = None
            pmid = None
            doi = None
            for child in article.findall('./front/article-meta/article-id'):
                id = sanitize_text(child.text)
                if(child.get('pub-id-type') == 'pmc'):
                    pmc = sanitize_text(child.text)
                elif(child.get('pub-id-type') == 'pmid'):
                    pmid = sanitize_text(child.text)
                elif(child.get('pub-id-type') == 'doi'):
                    doi = sanitize_text(child.text)
            if(pmc): id = pmc
            elif(pmid): id = pmid
            elif(doi): id = doi

            # Stops inputting if article
            # Checks if the article is pullable or not
            if(not article.find('./body')):
                skipped_articles.append(id)
                continue

            # Converting abstract and body to proper format
            body = sanitize_text(ET.tostring(article.find('./body'), encoding='utf-8', method='text').decode('utf-8'))
            text = body

            if(article.find('./front/article-meta/abstract')):
                abstract = sanitize_text(ET.tostring(article.find('./front/article-meta/abstract'), encoding='utf-8', method='text').decode('utf-8'))
                text = abstract + ' ' + body 

            # Json Array that holds the title, id, and text
            query_array = {
                "id": id,
                "genus": query,
                "text": text
            }

            # Creating file
            with open(dirname + '/' + query + '_' + id + '.json', 'w', encoding='utf-8') as f:
                json.dump(query_array, f, indent=3)


    # Creates the skipped_articles.json file and/or updates itwith open('metadata/skipped_articles.json', 'r') as json_file:
    # 1: Creates file if doesn't exist,
    # 2: Reads json from file
    # 3: Creates new part of json and adds it or updates current 
    all_json = {}
    skipped_file = 'metadata/skipped_articles.json'


    if os.path.isfile(skipped_file) is False:
        with open(skipped_file, 'w') as json_file:
            json_file.write('{}')

    destination = 'backups/' + skipped_file.split('/')[1]
    shutil.copy(skipped_file, destination)

    with open(skipped_file, 'r') as json_file:
        all_json = json.load(json_file)
        # DEBUGGING: print(all_json)

    with open(skipped_file, 'w') as json_file:
        if(query in all_json):
            # DEBUGGING: print(skipped_articles)
            new_array = all_json[query]
            for item in skipped_articles:
                if(item not in new_array):
                    new_array.append(item)
            skipped_articles = new_array
            for key, value in all_json.items():
                if key == query:
                    all_json[key] = skipped_articles
        else:
            all_json.update({query : skipped_articles})
        json.dump(all_json,
            json_file,
            indent=4,
        )


# Sanitize text from articles into normal text with proper spacing.
# @params: text = text to be sanitized
def sanitize_text(text):
    text = re.sub(r"\s{2,}|(\n+)|(\r+)|(\t+)", " ", text.replace('\n', ' ').replace('\r', ' ').strip())
    text = text.encode('ascii', 'ignore').decode()

    return text

# Checks whether two lists have a common element
# @params: two lists
def common_data(list1, list2):
    result = False
  
    # traverse in the 1st list
    for x in list1:
  
        # traverse in the 2nd list
        for y in list2:
    
            # if one common
            if x == y:
                result = True
                return result            
    return result

def generate_status_report(file):
    origin_genus_file = 'metadata/genus_id_totals.txt'
    origin_genus_list = get_array(origin_genus_file)

    genus_file = 'metadata/genus_remainder.txt'
    genus_list = get_array(genus_file)

    with open('metadata/article_pulling_status.txt', 'w') as f:
        f.write('---TEMPLATE:---\n')
        f.write('Genus Completed: ' + str(len(origin_genus_list) - len(genus_list)) + '/' + str(len(origin_genus_list)) + '\n')
        f.write('Next Genus: ' + genus_list[0] + '\n\n')
        f.write('Detailed List:\n')

        for i in origin_genus_list[:(len(origin_genus_list) - len(genus_list))]:
            f.write('[X] - ' + i + '\n')
        for i in origin_genus_list[(len(origin_genus_list) - len(genus_list)):]:
            f.write('[ ] - ' + i + '\n')


# ------------------------------------------------------------

# Allow for modular data directory selection
# base_directory = 'D:/repos/fungi-paper-requests/'
origin_genus_file = 'metadata/genus_id_totals.txt'
genus_file = 'metadata/genus_remainder.txt'

directory = 'E:/fungidata/'

request_quantity = 50
# dirname = os.path.dirname(filename)
# if not os.path.exists(dirname):
#     os.makedirs(dirname)

# ------------------------------------------------------------
# STEP 1 - Import First List to New List to Count Remainder
# generate_job_list(origin_genus_file, genus_file)

# STEP 2 - Get ID's using list
# create_indicies(get_array('metadata/genus_remainder.txt'), directory)

# OPTIONAL - Generate data from IDs 
# compute_total_ids(get_array('metadata/genus_remainder.txt'), directory)

# STEP 3 - Get Papers from IDs
# Outer For Loop for going through the query list
genus_list = get_array(genus_file)
genus_list_copy = copy.deepcopy(genus_list)
for genus in genus_list:
    # Inner Loop to create articles
    print(genus + ': REQUESTS STARTED')
    base_index_array = get_index(genus, directory)

    # Check if already completed
    skipped_json = []
    with open('metadata/skipped_articles.json', 'r') as json_file:
        all_json = json.load(json_file)
    
    if(genus in all_json):
        for key, value in all_json.items():
            if key == genus:
                skipped_json = all_json[key]

    # ( len(os.listdir(directory + genus + "/") - 1) >= (len(base_index_array) ) * .8 ) and 
    if( (len(os.listdir(directory + genus + "/")) - 1) == (len(base_index_array) - len(skipped_json)) ):
        if(len(base_index_array) == 0):
            print(genus + ': NO ASSOCIATED IDS')
        else:
            print(genus + ': ALREADY COMPLETED')
        print('-----------------------')

        genus_list_copy.pop(0)
        with open(genus_file, 'w') as f:
            f.writelines('\n'.join(genus_list_copy))
    
        generate_status_report('metadata/article_pulling_status.txt')
        continue
    
    
    # Start of requesting
    # If the index has more than 100 IDs, do multiple requests
    if(len(base_index_array) > request_quantity):
        sum = 0
        for i in range(0, len(base_index_array), request_quantity):
            testing_array = base_index_array[i:i+request_quantity]
            sum += len(testing_array)

            if(common_data(testing_array, skipped_json)):
                print('Status of ' + genus + ': ' + str(sum) + '/' + str(len(base_index_array)) + ' already downloaded...')
                continue

            print('Status of ' + genus + ': ' + str(sum) + '/' + str(len(base_index_array)))
            create_articles_from_array(genus, testing_array, directory)
    # If the index has less than 100 IDs, do one request
    else:
        total = len(base_index_array)
        print('Status of ' + genus + ': ' + str(total) +'/' + str(total))
        create_articles_from_array(genus, base_index_array, directory)

    # Re-writes job list with completed genus and updates status
    print(genus + ': REQUESTS COMPLETED')
    print('-----------------------')

    genus_list_copy.pop(0)
    with open(genus_file, 'w') as f:
        f.writelines('\n'.join(genus_list_copy))

    generate_status_report('metadata/article_pulling_status.txt')

# ------------------------------------------------------------
