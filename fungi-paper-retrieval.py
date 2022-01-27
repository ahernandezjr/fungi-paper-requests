import requests

# Retrieving genus list
def import_init_file(origin_file_name, new_file_name):
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

# def find_ids():
# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=Amanita&retmax=20000&tool=funguild&email=stbates@purdue.edu
# File will have an implicit "\n", so use row.strip()


import_init_file("genus_final_list.txt", "genus_remainder.txt")

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