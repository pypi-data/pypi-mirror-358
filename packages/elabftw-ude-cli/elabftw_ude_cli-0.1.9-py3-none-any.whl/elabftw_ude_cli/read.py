# import statements
import json
import ssl
import requests
from . import config as Config
from . import config as Config

def print_json_nicely(data):
    for x in dict(data):
        print(f"{x}:{data[x]}")


def read_experiment(experiment_id=75, print_out=False):
    if Config.verbose >= 2:print_out=True
    endpoint = Config.base_url+"experiments/"+str(experiment_id)
    response = requests.get(endpoint, headers=Config.headers)
    data = response.json()
    if response.status_code == 200:
        # Request was successful
        if print_out: print_json_nicely(data)
    else:
        # Request failed
        print("Error:", response.status_code, response.text)
    return data
