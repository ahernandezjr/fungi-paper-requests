import requests

# Retrieving genus list
f = open("genus_final_list.txt", "r")

genus_list = []

for x in f:
    genus_list.append(x.split(":")[0])



# Request of paper and writing to file
# file = open("test.xml", "w")

# response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=8779134')

# file.write(response.text)

# file.close("test.xml")