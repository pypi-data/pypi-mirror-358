import json
import requests
from . import config as Config


def find_experiments(limit=15, offset=0):
    """
    We will use this function to extract all the experiments the USER has access to,
    and only the experiments that are not deleted.
    The while loop will do it recursively since the api can read only 100 entries at a time.
    :param limit: Since API can only read a specific number of experiments at time we will start with 15.
    :param offset: Initial offset since this functoin is called repeatedly its better to set this default to zero.
    :return: List of all experiments.
    """
    endpoint = Config.base_url + "experiments/"
    experiments = []
    while True:
        params = {'limit': limit, 'offset': offset}
        response = requests.get(endpoint, headers=Config.headers, params=params)
        data = response.json()
        #print(data)
        if response.status_code == 200:
            experiments.extend(data)
            if len(data) < limit:
                break
            offset += limit
        else:
            print("Error:", response.status_code, response.text)
            break
    if Config.verbose >= 1: print(f"Total experiments fetched: {len(experiments)}")
    return experiments


def filter_experiments(term="Untitled"):
    """
    This functon can be used to filter the list acquired by the find experiments function to actually
    search for the experiment/s of interest.
    :param term: The search term to be used.
    :return: A filtered list of list the experiment IDs of matching experiments and a separate list of just names
    """
    json_obj=find_experiments()
    filtered_IDS=list()
    filtered_names=list()
    for experiment in json_obj:
        if str(experiment["title"]).__contains__(term):
            id=experiment["id"]
            name=experiment["title"]
            #print(f"found {name}")
            filtered_names.append(name)
            filtered_IDS.append(id)
    #print(filtered_list)
    if Config.verbose >= 1: print(f"filterd {len (filtered_IDS)} experiments with keyword {term}")
    return filtered_IDS, filtered_names
