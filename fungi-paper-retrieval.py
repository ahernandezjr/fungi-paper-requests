from posixpath import dirname
import shutil
import os
import requests
import xml.etree.ElementTree as ET
from time import sleep

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
    with open(new_file_name, "w") as f:
        for row in origin_array:
            f.write(row + "\n")

    source = new_file_name
    destination = "backups/" + new_file_name
    shutil.copy(source, destination)

# Create index files with ID's for all papers of a genus
# @params: query = genus-to-be-searched
def get_ids(list_file):
    # First and second parts of the url
    BASE_URL1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term='
    BASE_URL2 = '&retmax=1000000'

    # Obtain Query List for folders and indexes
    query_list = []
    with open(list_file) as f:
        for row in f:
            query_list.append(row.strip())

    # 
    for query in query_list[2570:]:
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
            # Just a test file to see content-type
            with open("test.xml", "w") as test:
                test.write(response.headers.get('Content-Type'))
            
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

def compute_total_ids(genus_list):
    total = 0
    genus_array = []

    with open(genus_list, mode='r', encoding='utf-8') as genus_file:
        # Create array of genus list from the file
        for genus in genus_file:
            genus_array.append(genus.strip())

    with open('metadata/genus_id_totals.txt', 'w') as id_file:
        for genus in genus_array:
            # Gets file location of index for genus
            filename = 'data/' + genus + '/'
            dirname = os.path.dirname(filename)

            # Gets total ID's in file and does calculations and writing to total file
            this_total = sum(1 for line in open(dirname + '/' + genus + '_index.txt'))
            total += this_total
            print(total)
            id_file.write(genus + ':' + str(this_total) + '\n')
        
        id_file.write('Total: ' + str(total) + '\n')




# Pull all papers from index for genus
# def get_papers(genus_name):
    # Request of paper and writing to file
    # file = open("test.xml", "w")

    # response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=8779134')
    # file.write(response.text)
    # file.close("test.xml")


# Import First List to New List to Count Remainder
    # import_init_list("metadata/genus_final_list.txt", "metadata/genus_remainder.txt")

# Get ID's using list
    # get_ids("metadata/genus_remainder.txt")

compute_total_ids('metadata/genus_remainder.txt')