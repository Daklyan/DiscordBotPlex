import json
import requests
import time

class Trakt:
    def __init__(self):
        self.TRAKT_API_URL = "https://api.trakt.tv"
        self.access_token = ""
        self.refresh_token = ""
        self.expire_date = 0
        with open('config.json') as f:
            data = json.load(f)
            self.trakt_client_id = data['trakt_client_id']
            self.trakt_client_secret = data['trakt_client_secret']
            self.lists = data['lists']
            self.username = data['trakt_username']

        try:
            with open('token_data.json') as f:
                data = json.load(f)
                self.access_token = data['access_token']
                self.refresh_token = data['refresh_token']
                self.expire_date = data['expire_date']
        except IOError:
            print("Can't open token_data.json")

        self.HEADERS = {
            "Content-type": "application/json",
            "trakt-api-key": self.trakt_client_id,
            "trakt-api-version": "2",
            "Authorization": f'Bearer {self.access_token}'
        }


    def login(self):
        # Getting authorization code
        r = requests.post(url=f'{self.TRAKT_API_URL}/oauth/device/code', json={"client_id": self.trakt_client_id}, headers=self.HEADERS)
        data_device_code = r.json()

        # User confirm connection with his browser / phone
        input(f'Enter {data_device_code["user_code"]} at https://trakt.tv/activate then press the Enter key...')

        # Exchanging authorization code with access token
        token_body = {
            "code": data_device_code['device_code'],
            "client_id": self.trakt_client_id,
            "client_secret": self.trakt_client_secret
        }
        r = requests.post(url=f'{self.TRAKT_API_URL}/oauth/device/token', json=token_body, headers=self.HEADERS)
        data_device_token = r.json()

        # Saving new data
        self.access_token = data_device_token['access_token']
        self.refresh_token = data_device_token['refresh_token']
        self.expire_date = data_device_token['created_at'] + data_device_token['expires_in']

        file_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expire_date": self.expire_date
        }
        
        file_data_json = json.dumps(file_data)
        with open("token_data.json", "w") as f:
            f.write(file_data_json)
        
        # Updating headers variable
        self.HEADERS = {
            "Content-type": "application/json",
            "trakt-api-key": self.trakt_client_id,
            "trakt-api-version": "2",
            "Authorization": f'Bearer {self.access_token}'
        }

        return r.status_code


    def refresh_login(self):
        # Exchanging refresh token with new access token
        body = {
            "refresh_token": self.refresh_token,
            "client_id": self.trakt_client_id,
            "client_secret": self.trakt_client_secret,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "refresh_token"
        }

        r = requests.post(url=f'{self.TRAKT_API_URL}/oauth/token', json=body, headers=self.HEADERS)
        data = r.json()

        # Saving new data
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expire_date = data['created_at'] + data['expires_in']

        file_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expire_date": self.expire_date
        }

        file_data_json = json.dumps(file_data)
        with open("token_data.json", "w") as f:
            f.write(file_data_json)
        
        # Updating headers variable
        self.HEADERS = {
            "Content-type": "application/json",
            "trakt-api-key": self.trakt_client_id,
            "trakt-api-version": "2",
            "Authorization": f'Bearer {self.access_token}'
        }

        return r.status_code


    def search(self, category, query):
        if(category != "movie" and category != "show"):
            return -1
        r = requests.get(url=f'{self.TRAKT_API_URL}/search/{category}?query={query}', headers=self.HEADERS)
        return r.json()


    def add_to_list(self, category, query_name):
        type = ""
        if category == "movie" or category == "animation":
            type = "movie"
        else:
            type = "show"
 
        query = self.search(type, query_name)
        query_id = query[0][type]['ids']['trakt']
        item = {
            f'{type}s': [
                {
                    "ids": {
                        "trakt": query_id
                    }
                }
            ] 
        }
        
        summary_url = f'{self.TRAKT_API_URL}/{type}s/{query_id}?extended=full'
        r = requests.get(url=summary_url, headers=self.HEADERS)
        query_summary = r.json()
        query[0][type]['summary'] = query_summary["overview"]
        query[0][type]['rating'] = query_summary["rating"]
        
        if type == "movie":
            query[0][type]['runtime'] = query_summary["runtime"]
        else: 
            seasons_url = f'{self.TRAKT_API_URL}/{type}s/{query_id}/seasons'
            r = requests.get(url=seasons_url, headers=self.HEADERS)
            query_seasons = r.json()
            query[0][type]["nb_seasons"] = query_seasons[-1]["number"]

        list_url = f'{self.TRAKT_API_URL}/users/{self.username}/lists/{self.lists[category]}/items'
        r = requests.post(url=list_url, json=item, headers=self.HEADERS)

        if r.status_code >= 200 and r.status_code < 300:
            return query[0], generate_trakt_url(type, query[0][type]['ids']['slug'])
            # return f'{query_name} added to {self.lists[category]}', self.generate_trakt_url(type, query[0][type]['ids']['slug'])
        elif r.status_code >= 400:
            return f'Status code {r.status_code}: {r.reason}', None


    def remove_from_list(self, category, query_name):
        type = ""
        if category == "movie" or category == "animation":
            type = "movie"
        else:
            type = "show"

        query = self.search(type, query_name)
        query_id = query[0][type]['ids']['trakt']
        item = {
            f'{type}s': [
                {
                    'ids': {
                        'trakt': query_id
                    }
                }
            ]
        }

        list_url = f'{self.TRAKT_API_URL}/users/{self.username}/lists/{self.lists[category]}/items/remove'

        r = requests.post(url=list_url, json=item, headers=self.HEADERS)

        if r.status_code >= 200 and r.status_code < 300:
            return query[0], generate_trakt_url(type, query[0][type]['ids']['slug'])
        elif r.status_code >= 400:
            return f'Status code {r.status_code}: {r.reason}', None

        elif r.status_code >= 400:
            return f'Status code {r.status_code}: {r.reason}', None

            
    def check_access_token(self):
        current_timestamp = time.time()
        if self.access_token and current_timestamp >= self.expire_date:
            self.refresh_login()
        elif not self.access_token:
            self.login()


def generate_trakt_url(type, slug):
    return f'https://trakt.tv/{type}s/{slug}'
