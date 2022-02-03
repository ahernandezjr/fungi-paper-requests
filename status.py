# Create an array from a file
# @params: file = file to pull array from
def get_array(file):
    array = []
    with open(file, mode='r', encoding='utf-8') as array_file:
        array = array_file.read().splitlines()

    return array


# Manually updates the 'status.txt' file

# Shows the current status showing:
# Genus done so far / Total Genus at start

origin_genus_file = 'metadata/genus_id_totals.txt'
origin_genus_list = get_array(origin_genus_file)

genus_file = 'metadata/genus_remainder.txt'
genus_list = get_array(genus_file)

with open('metadata/status.txt', 'w') as f:
    f.write('---TEMPLATE:---\n')
    f.write('Genus Completed: ' + str(len(origin_genus_list) - len(genus_list)) + '/' + str(len(origin_genus_list)) + '\n')
    f.write('Next Genus: ' + genus_list[0] + '\n\n')
    f.write('Detailed List:\n')

    for i in origin_genus_list[:(len(origin_genus_list) - len(genus_list))]:
        f.write('[X] - ' + i + '\n')
    for i in origin_genus_list[(len(origin_genus_list) - len(genus_list)):]:
        f.write('[ ] - ' + i + '\n')