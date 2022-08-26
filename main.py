import json
import discord
import time

from discord_utils import MyClient
from trakt_utils import Trakt

with open('config.json') as f:
    data = json.load(f)
    token = data['discord_bot_token']

current_timestamp = time.time()

intents = discord.Intents.default()
intents.message_content = True

# Trakt
trakt = Trakt()
if not trakt.access_token:
    trakt.login()
elif(trakt.access_token and current_timestamp >= trakt.expire_date):
    trakt.refresh_login()

tmp = trakt.search("movie", "shrek")
print(tmp)

client = MyClient(intents=intents)
client.run(token)
