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


# Updates JSON file to add unrelated articles
# @params: unrelated_articles = file that holds the unrelated articles, genus = name of genus for stat tracking
def update_json(unrelated_articles, genus, source):
    # Start of filtering process
    all_json = {}
    unrelated_file = 'metadata/unrelated_articles' + source + '.json'

    if os.path.isfile(unrelated_file) is False:
        with open(unrelated_file, mode='w') as json_file:
            json_file.write('[]')

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


# Searches a file to see if it contains keywords
# @params: unrelated_articles = file that holds the unrelated articles, genus = name of genus for stat tracking
# @return: article_id = returns the id of the file
def get_unrelated_id(file):
    # Set Mode
    mode = 0
    if(file.split('_')[0] == 'wiki'):
        mode = 1
    
    if (mode==1):
        # 'genus' changes depending on if ncbi or wiki
        json_data = {}
        with open(directory + file, mode='r', encoding='utf-8') as f:
            json_data = json.load(f)

        if not any( (word.casefold() in json_data[0]['text'].casefold()) for word in required_words ):
            # print(article_id)
            return file

    else:
        print('hi')

        # 'genus' changes depending on if ncbi or wiki
        genus = file.split('_')[0] + '/'

        if (file != genus + '_index.txt'):
            json_data = {}
            with open(directory + genus + file, mode='r', encoding='utf-8') as f:
                json_data = json.load(f)

            if not any( (word.casefold() in json_data['text'].casefold()) for word in required_words ):
                article_id = file.split('_')[1].split('.')[0]
                # print(article_id)
                return article_id


# Loops through an array and gets corresponding files using the get_unrelated_ids and adds to json with update_json
# @params: array = base array for data, total_articles_count = gets the updated amount of articles, unrelated_article_count = gets the updated amount of articles that are unrelated
def get_ncbi_data(array, total_articles_count, unrelated_article_count):
    pool = Pool(16)
    for genus in array:
        unrelated_articles = []

        print('-----------------------------')
        print(genus + ' Data:')

        total_articles_count += len(os.listdir(directory + genus + "/")) - 1
        print('Total Articles: ' + str(total_articles_count))
        
        # Loop process to get totals and IDs
        # get_unrelated_ids(For every item in os.listdir) and return x if x is not empty
        unrelated_articles = list([ x for x in pool.map(get_unrelated_id, os.listdir(directory + genus + "/")) if x is not None])

        unrelated_article_count += len(unrelated_articles)

        print('Unrelated Articles: ' + str(len(unrelated_articles)))
        print('\tTotal: ' + str(unrelated_article_count))

        update_json(unrelated_articles, genus, '_ncbi')

    pool.close()
    pool.join()


def get_wiki_data(total_articles_count, unrelated_article_count):
    unrelated_articles = []

    print('-----------------------------')
    print('Wiki Data:')

    total_articles_count = len(os.listdir(directory))
    print('Total Articles: ' + str(total_articles_count))
    
    # Loop process to get totals and IDs
    # get_unrelated_ids(For every item in os.listdir) and return x if x is not empty
    unrelated_articles = list([ x for x in map(get_unrelated_id, os.listdir(directory)) if x is not None])

    unrelated_article_count += len(unrelated_articles)

    print('Unrelated Articles: ' + str(len(unrelated_articles)))
    print('\tTotal: ' + str(unrelated_article_count))

    update_json(unrelated_articles, 'all', '_wiki')


def progress_bar(current, total, bar_length = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces  = ' ' * (bar_length - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')


# Files that contain lines for arrays
origin_genus_file = 'metadata/genus_id_totals.txt'
data_analysis_file_ncbi = 'metadata/data_analysis_ncbi.txt'
data_analysis_file_wiki = 'metadata/data_analysis_wiki.txt'

# Base Directory where data will be pulled from
# directory = 'E:/fungidata/'
directory = 'E:/wikipedia_json_files/'

# List of words to search for
required_words = ['fungi', 'fungus', 'mushroom', 'mushrooms', 'genus']

# Updating count for files
total_articles_count_ncbi = 0
unrelated_article_count_ncbi = 0
total_articles_count_wiki = 0
unrelated_article_count_wiki = 0

# Main function - only activates within main thread (to prevent multi-threading recursion)
if __name__ == '__main__':
    # get_ncbi_data(get_array(origin_genus_file), total_articles_count_ncbi, unrelated_article_count_ncbi)

    # with open(data_analysis_file_ncbi, mode='w') as f:
    #     f.write('Total Articles: ' + str(total_articles_count_ncbi) + '\n' + 'Unrelated Articles: ' + str(unrelated_article_count_ncbi) + '\n')

    # i = 0
    # print('Sanitizing documents: ')
    # for file in os.listdir(directory):
    #     progress_bar(i, len(os.listdir()))
    #     sanitize_documents(file)
    #     i += 1

    get_wiki_data(total_articles_count_wiki, unrelated_article_count_wiki)

    with open(data_analysis_file_wiki, mode='w') as f:
        f.write('Total Articles: ' + str(total_articles_count_wiki) + '\n' + 'Unrelated Articles: ' + str(unrelated_article_count_wiki) + '\n')


    # print(total_articles_count)
