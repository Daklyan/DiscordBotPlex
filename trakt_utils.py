import json
import requests

from trakt import core
from trakt import users
from trakt import init


with open('config.json') as f:
    data = json.load(f)
    trakt_client_id = data['trakt_client_id']
    trakt_client_secret = data['trakt_client_secret']
    lists = data['lists']
    username = data['trakt_username']



core.AUTH_METHOD = core.OAUTH_AUTH
core.OAUTH_TOKEN = init(username, client_id=trakt_client_id, client_secret=trakt_client_secret, store=True)
my_user = users.User(username)
print(my_user.lists)

def check_trakt_url(url):
    request = requests.get(url=url)
    if(request.status_code == 200):
        return True
    elif(request.status_code == 404):
        return False
    else:
        print(request.status_code)


def add_to_trakt_list(list, url):
    if(list in lists):
        pass   
    return "List not found"
