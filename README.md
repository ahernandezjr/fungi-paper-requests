# fungi-paper-requests
Script to retrieve related papers to fungi (or any other list of query terms). This repository was created with a specific case in mind:

  A list of genera related to fungi is used to pull their corresponding articles from NCBI (and, not in this repo, Wikipedia).

  The articles are filtered under their genus name and eventually changed to their 'guild' name to better correspond functionality for later analysis.

  Articles begin in the JSON format for readability, but later changed to CSV for better processing after separation into 'token',
    which are identified by a Machine Learning algorithm focused on the concept Natural Language Processing.

  This research is sanctioned and funded by Purdue under professors Dr. Scott Bates and Dr. Ricardo Calix.

  This repository was created and is maintained by Alexander Hernandez Jr and is intended to become a free-use, article-pulling tool to obtain 
    data from NCBI in an easy way with just a few modifications.


  Type: Python Script
  

  Scripts: {

    'all_files_modify.py' - ambiguous script meant for running individual, reusable scripts to affect all files in directory,

    'data_analysis.py'    - runs data analysis over a variety of functions like getting unrelated articles or data for ncbi/wiki articles,

    'paper_retrieval.py'  - main function primarily used in a 3-step process to obtain articles from a list of query terms,

    'status.py'           - quick update for the status of 'paper_retrieval.py', mainly used when the process is cancelled,

    'transfer_data.py'    - contains functions relating to transfering data while filtering or not

  }
  

  Dependencies: {

    copy

    csv

    json

    multiprocessing

    numpy

    os

    re

    requests

    shutil

    time

    xml.etree.ElementTree

  }

  
  Output Files: {

    "article_pulling_status.txt"    - status file for article pulling for fungi-paper-retrieval.py,

    "data_analysis_ncbi.txt"        - analysis file showing total articles and unrelated articles that will be omitted,

    "data_analysis_wiki.txt"        - analysis file showing total articles and unrelated articles that will be omitted,

    "genus_final_list.txt"          - init fungi genus list,

    "genus_id_totals.txt"           - original list of pullable articles from NCBI with their total articles,
    
    "genus_remainder.txt"           - remainder of fungi between success script runs,
    
    "guild_no_results_file.txt"     - marks files that do not return a corresponding guild relating to genus name from the FunGuild database,
    
    "guild_results_file.txt"        - marks files that do return a corresponding guild relating to genus name from the FunGuild database,

    "unrelated_articles_ncbi.json"  - json identifying which id's from the ncbi list return 'unrelatedness' and to ignore them,
    
    "unrelated_articles_wiki.json"  - json identifying which id's from the wiki list return 'unrelatedness' and to ignore them,

  }
