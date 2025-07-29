# import statements
import json
import ssl
import requests
from . import config as Config
from . import search as esearch


def change_visibility(id, change_key, changed_value):
    url=Config.base_url+f"experiments/"+str(id)
    Config.headers['Content-Type']='application/json'

    # Define the data to be sent in the request body
    data = {change_key: changed_value}
    if Config.verbose >= 1: print(json.dumps(data))
    # Send the PATCH request
    response = requests.patch(url, headers=Config.headers, data=json.dumps(data))
    if Config.verbose >= 1: print(response.json())
    # Check the response status code
    if response.status_code == 200:
        if Config.verbose >= 1: print("Experiment updated successfully.")
    elif response.status_code == 400:
        print("Bad request. Check if the request body is correctly formatted.")
    else:
        print("Failed to update experiment. Status code:", response.status_code)
        print("Response:", response.text)


def modify_ids_list(new_list,change_key,changed_value):
    for exp_id in new_list:
        change_visibility(exp_id,change_key,changed_value)
