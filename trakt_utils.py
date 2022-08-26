import json
import requests

class Trakt:
    def __init__(self):
        self.TRAKT_API_URL = "https://api.trakt.tv"
        self.REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

        with open('config.json') as f:
            data = json.load(f)
            self.trakt_client_id = data['trakt_client_id']
            self.trakt_client_secret = data['trakt_client_secret']
            self.lists = data['lists']
            self.username = data['trakt_username']

        self.HEADERS = {
            "Content-type": "application/json",
            "trakt-api-key": self.trakt_client_id,
            "trakt-api-version": "2"
        }

    def login(self):
        r = requests.post(url=f'{self.TRAKT_API_URL}/oauth/device/code', json={"client_id": self.trakt_client_id}, headers=self.HEADERS)

        data_device_code = r.json()
    
        input(f'Enter {data_device_code["user_code"]} at https://trakt.tv/activate then press any key...')

        token_body = {
            "code": data_device_code['device_code'],
            "client_id": self.trakt_client_id,
            "client_secret": self.trakt_client_secret
        }
        r = requests.post(url=f'{self.TRAKT_API_URL}/oauth/device/token', json=token_body, headers=self.HEADERS)
        data_device_token = r.json()
        print(r)


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
