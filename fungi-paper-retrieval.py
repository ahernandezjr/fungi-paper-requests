from posixpath import dirname
import shutil
import os
from time import sleep
import numpy as np
import re
import requests
import xml.etree.ElementTree as ET
import json

# Retrieving genus list
# WARNING: Only used the first time
# @params: data from origin file inserted into new file
def import_init_list(origin_file_name, new_file_name):
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
def get_ids(query_list):
    # First and second parts of the url
    BASE_URL1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term='
    BASE_URL2 = '&retmax=1000000'

    # Start of looping through genus_list to get all ids
    for query in query_list:
        sleep(0.35)
        query = query.strip()

        # Make Directory if !exists
        filename = "data/" + query + "/"
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
                with open("metadata/index_log.txt", "a+") as index_log:
                    if (f"No ID results for: {query}\n" not in index_log):
                        index_log.write(f"No ID results for: {query}\n")
                continue

            for id in root.findall('IdList/Id'):
                f.write(id.text + "\n")


# Compute total number of IDs found for data analysis
# @params: genus_list = list of the genus to view index files
def compute_total_ids(genus_array):
    # Variable for sum
    total = 0

    with open('metadata/genus_id_totals.txt', 'w') as id_file:
        for genus in genus_array:
            # Gets file location of index for genus
            filename = 'data/' + genus + '/'
            dirname = os.path.dirname(filename)

            # Gets total ID's in file and does calculations and writing to total file
            this_total = sum(1 for line in open(dirname + '/' + genus + '_index.txt'))
            total += this_total
            id_file.write(genus + ':' + str(this_total) + '\n')
        
        id_file.write('Total: ' + str(total) + '\n')
    

# Gets index of a genus from its folder/file
# @params: query_list = list of genuses (queries)) to be searched and data pulled
def get_index(query):
    filename = 'data/' + query + '/'
    dirname = os.path.dirname(filename)
    index_file_location = dirname + '/' + query + '_index.txt'

    # Takes all IDs from index of query
    with open(index_file_location) as index_file:
        index_array = index_file.read().splitlines()

    return index_array


# Get papers from a list of genuses to be searched
# @params: query = genus, index_array = list of ID's to get papers from
def get_papers_from_list(query, index_array):
    print("This array has a length of " + str(len(index_array)))

    # Make Directory if !exists
    filename = "data/" + query + "/"
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='
    url_append = ','.join(index_array)
    search_url = BASE_URL + url_append

    # Gets response 
    response = requests.get(search_url)
    root = ET.fromstring(response.text)

    # Inner for loop for adding papers from requests
    if(len(index_array) == 1):
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

        # Converting body to proper format
        text = sanitize_text(ET.tostring(root.find('.//body'), encoding='utf-8', method='text').decode('utf-8'))
        text = re.sub(r"\s{2,}", " ", text.replace('\n', ' ').replace('\r', ' ').strip())

        # Json Array that holds the title, id, and text
        query_array = {
            "id": id,
            "genus": query,
            "text": text
        }

        # Creating file
        with open(dirname + "/" + query + "_" + id + ".json", "w") as f:
            f.write(json.dumps(query_array, indent=3))
            
    else:
        # IMPORTANT --------------------------------------




        # Add situation where this message appears and the front is only seeable:
        # <!-- The publisher of this article does not allow downloading of the full text in XML form. -->
        # IDEAS: check length of 'article'





        # IMPORTANT --------------------------------------

        x = 0
        for article in root.findall('article'):
            x+=1
            print("article: " + str(x))
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

            # Converting body to proper format
            text = sanitize_text(ET.tostring(article.find('./body'), encoding='utf-8', method='text').decode('utf-8'))
            text = re.sub(r"\s{2,}", " ", text.replace('\n', ' ').replace('\r', ' ').strip())

            # Json Array that holds the title, id, and text
            query_array = {
                "id": id,
                "genus": query,
                "text": text
            }

            # Creating file
            with open('article' + str(x) + '.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(query_array, indent=3))
    
    return


def sanitize_text(text):
    text = re.sub(r"\s{2,}|(\n+)|(\r+)|(\t+)", " ", text)
    return text




# ------------------------------------------------------------
# ------------------------------------------------------------
# STEP 1 - Import First List to New List to Count Remainder
    # import_init_list("metadata/genus_final_list.txt", "metadata/genus_remainder.txt")

# STEP 2 - Get ID's using list
    # get_ids(get_array('metadata/genus_remainder.txt'))

# OPTIONAL - Generate data from IDs 
    # compute_total_ids(get_array('metadata/genus_remainder.txt'))

# STEP 3 - Get Papers from IDs

# Outer For Loop for going through the query list
# for x in range(len(job_array)):
query_array = []
with open('metadata/genus_remainder.txt') as f:
    query_array = f.read().splitlines()


# for query in query_array:
# query ='aabaarnia'
query = 'Aaosphaeria'
get_papers_from_list(query, get_index(query))

    # query = query_array.pop(0)


    # If less than 100 ID's, request once
    # ADD ------ IF only 1 article, it needs to be a level higher
    

    # else:
    #     for x in index_array:
    #         response = requests.get()
    #         file.write(response.text)
    #         file.close("test.xml")
    
    
        # Search for articles with item
        # Check how many ids are in item index

        
    # ENABLE ONCE DONE TESTING
    # Re-writes the job_file to update it
    # with open(job_list, 'w') as f:
    #     f.writelines(job_array)


# ------------------------------------------------------------
# ------------------------------------------------------------
