import requests

# Retrieving genus list
# WARNING: Only used the first time
# @params: data from origin file inserted into new file
def import_init_list(origin_file_name, new_file_name):
    # Open origin file
    with open(origin_file_name, mode='r', encoding='utf-8') as origin_file:
        # Create array of genus in the file
        origin_array = []
        for x in origin_file:
            origin_array.append(x.split(":")[0])

    # Copy 'Remainder' file to "/backups/"

    # Create new "remainder" file
    with open(new_file_name, "w") as f:
        for row in origin_array:
            f.write(row + "\n")

# Create index files with ID's for all papers of a genus
# @params: query = genus-to-be-searched
def get_ids(query):
    BASE_URL1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term='
    # Add params so that it takes the first 20000 of an ordered list so the next 20000 can be taken
    BASE_URL2 = '&retmax=20000&tool=genus_data&email=herna309@pnw.edu'

    # Use PMID

    # Automated Query from file (not input) -
    #   File will have an implicit "\n", so use row.strip()

    # While response.length == 20000
    #   Add first 20000 to index file
    #   Take next 20000 and add to index
    #   Repeat until ids < 20000

    # with open(genus_name + "_index.txt) as f"
    while():
        search_url = query.join([BASE_URL1, BASE_URL2])
        response = requests.get(search_url)

        # Write ID's to file index /data/ within genus_name folder 


# Pull all papers from index for genus
# def get_papers(genus_name):



import_init_list("genus_final_list.txt", "genus_remainder.txt")

f = open("genus_remainder.txt")
array = []
for row in f:
    array.append(row)

print(array[-1].strip())
print(len(array))


# Request of paper and writing to file
# file = open("test.xml", "w")

# response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=8779134')

# file.write(response.text)

# file.close("test.xml")