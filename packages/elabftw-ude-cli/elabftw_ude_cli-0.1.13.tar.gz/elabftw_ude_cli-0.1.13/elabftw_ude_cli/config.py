########Configure Server and API_KEYS########
instructions="""
Some instructions:

verbose is to define how much output to print in stdout (normal terminal output) where:
0: for no verbose, 1: for status messages, and 2: for everything
[errors are always printed]

Next is two important things:
1.servers use this dictionary of dictionaries to define your server the format of each entry is:
    "Name": {"url":<url of your server>, "api_key":<your api_key>},
        Name can be anything you choose but stay consistent please
        <url of your server> the link/url/web-address of the elab server you normally use in your browser
        <your api_key> please check out the readme to see how to make you key (basically settings->api keys -> generate)

2.server_to_use -> this is the name of the server you have chosen to use I have included this functionality to support
those who have multiple servers and teams they are managing or are part of and is particularly useful for developers
and managers. If nothing is entered or a key used here is not in the servers definition then the first entry of the
server list will be used by default.
"""


verbose=1
servers = {
    "test_server": {"url": "<<url1>>",
                    "api_key": "<<api_key>>"},
    "prod_server_team1": {"url": "<<url2>>",
                          "api_key": "<<api_key>>"},
    "prod_server_team_2": {"url": "<<url2>>",
                           "api_key": "<<api_key>>"},
}
server_to_use = "<server_name_to_use>"



#####Nothing to change below this line unless you fully understand what you are doing"#########
##function to find location of current file to tell user to change the keys
def get_config_file_path():
    """
    Returns the path to the user's elabftw_ude_cli config.py file.
    """
    import os
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        create_persistent_config()
    return os.path.abspath(config_path)

#function to create a persistent config_file:
def create_persistent_config(force=False):
    """
    Creates a default config.json file in the same directory as this config.py.
    If force=True, it will overwrite any existing file.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    if os.path.exists(config_path) and not force:
        print(f"Config file already exists at {config_path}")
        return

    config_data = {
        "__instructions": "Some instructions in config.py can be accessed at: elabftw-cli --config-path",
        "verbose": 1,
        "servers": {
            "test_server": {"url": "<<url1>>", "api_key": "<<api_key>>"},
            "prod_server_team1": {"url": "<<url2>>", "api_key": "<<api_key>>"},
            "prod_server_team_2": {"url": "<<url2>>", "api_key": "<<api_key>>"}
        },
        "server_to_use": "test_server"
    }

    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)

    print(f"Created default config.json at {config_path}")
    print(instructions)
    return config_path

##reading from json if exists:
import os
import json
config_check=os.path.dirname(__file__)+"/config.json"
if os.path.exists(config_check):
    with open(config_check, 'r') as f:
        config_file_data=json.load(f)
    verbose=config_file_data["verbose"]
    servers=config_file_data["servers"]
    server_to_use = config_file_data["server_to_use"]
#server definition
try:
    if not server_to_use: server_to_use = list(servers.keys())[0]
    if not server_to_use in list(servers.keys()):
        import os

        first_key = list(servers.keys())[0]
        print(f"Warning {server_to_use} not defined in servers using {list(servers.keys())[0]} instead. "
              f"(the first entry in the servers dictionary)\n Hint: To supress this errorchange <<server_to_use>> "
              f"in the config file at{os.path.abspath(__file__)} to the first entry of the servers ditionary "
              f"(currently: {first_key} )")
        server_to_use = list(servers.keys())[0]
except NameError:
    server_to_use = list(servers.keys())[0]
except KeyError:
    server_to_use = list(servers.keys())[0]

#base_url definition
base_url_base = servers[server_to_use]["url"]
base_url = base_url_base + "/api/v2/"

# verifying if the url has been changed to reflect actual url:
if str(base_url).startswith("<"):
    import os
    created_p=create_persistent_config()
    message = f"""
    This seems to be your first use please edit the config file at {config_check} to add your api_keys and the server url.
    """
    if not created_p: print(instructions)
    exit(message)

##key definition
api_key = servers[server_to_use]["api_key"]
headers = {'Authorization': api_key}



#############End Config######################
