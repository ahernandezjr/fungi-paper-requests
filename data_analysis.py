import os
import json
import shutil
from multiprocessing import Pool

# Create an array from a file
# @params: file = file to pull array from
def get_array(file):
    array = []
    with open(file, mode='r', encoding='utf-8') as array_file:
        array = array_file.read().splitlines()

    for index, item in enumerate(array):
        if (item.split(':')[0] == 'Total'):
            array.pop(index)
            if (index >= len(array)):
                break
        array[index] = item.split(':')[0]

    return array


def update_json(unrelated_articles, genus):
    # Start of filtering process
    all_json = {}
    unrelated_file = 'metadata/unrelated_articles.json'

    if os.path.isfile(unrelated_file) is False:
        with open(unrelated_file, 'w') as json_file:
            json_file.write('{}')

    destination = 'backups/' + unrelated_file.split('/')[1]
    shutil.copy(unrelated_file, destination)

    with open(unrelated_file, 'r') as json_file:
        all_json = json.load(json_file)
        # DEBUGGING: print(all_json)

    with open(unrelated_file, 'w') as json_file:
        if(genus in all_json):
            # DEBUGGING: print(unrelated_articles)
            new_array = all_json[genus]
            for item in unrelated_articles:
                if(item not in new_array):
                    new_array.append(item)
            unrelated_articles = new_array
            for key, value in all_json.items():
                if key == genus:
                    all_json[key] = unrelated_articles
        else:
            all_json.update({genus : unrelated_articles})
        json.dump(all_json,
            json_file,
            indent=4,
        )


def get_unrelated_ids(file):
    genus = file.split('_')[0]
    if (file != genus + '_index.txt'):
        json_data = {}
        with open(directory + genus + "/" + file) as f:
            json_data = json.load(f)
        if not any( (word.casefold() in json_data['text'].casefold()) for word in required_words ):
            article_id = file.split('_')[1].split('.')[0]
            # print(article_id)
            return article_id


def iterate_genus_array(array, total_articles_count, unrelated_article_count):
    pool = Pool(16)
    for genus in array:
        unrelated_articles = []

        print('-----------------------------')
        print(genus + ' Data:')

        total_articles_count += len(os.listdir(directory + genus + "/")) - 1
        print('Total Articles: ' + str(total_articles_count))
        
        # Loop process to get totals and IDs
        unrelated_articles = list([ x for x in pool.map(get_unrelated_ids, os.listdir(directory + genus + "/")) if x is not None])

        unrelated_article_count += len(unrelated_articles)

        print('Unrelated Articles: ' + str(len(unrelated_articles)))
        print('\tTotal: ' + str(unrelated_article_count))

        update_json(unrelated_articles, genus)

    pool.close()
    pool.join()

origin_genus_file = 'metadata/genus_id_totals.txt'
data_analysis_file = 'metadata/data_analysis.txt'

directory = 'E:/fungidata/'

required_words = ['fungi', 'fungus', 'mushroom', 'mushrooms', 'genus']

total_articles_count = 0
unrelated_article_count = 0

if __name__ == '__main__':
    iterate_genus_array(get_array(origin_genus_file), total_articles_count, unrelated_article_count)

    with open(data_analysis_file, 'w') as f:
        f.write('Total Articles: ' + str(total_articles_count) + '\n' + 'Unrelated Articles: ' + str(unrelated_article_count) + '\n')
    # print(total_articles_count)
