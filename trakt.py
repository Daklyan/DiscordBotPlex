import json

TRAKT_API_URL = "https://api.trakt.tv"

with open('config.json') as f:
    data = json.load(f)
    trakt_client_id = data['trakt_client_id']
    trakt_client_secret = data['trakt_client_secret']


