import json
import discord
import time

from trakt_utils import Trakt

with open('config.json') as f:
    data = json.load(f)
    token = data['discord_bot_token']
    channel_id = data['bot_channel_id']

current_timestamp = time.time()

# Trakt
trakt = Trakt()
if not trakt.access_token:
    trakt.login()
elif(trakt.access_token and current_timestamp >= trakt.expire_date):
    trakt.refresh_login()

class MyClient(discord.Client):
    async def on_message(self, message):
        if message.channel.id == int(channel_id) and message.content.startswith('!'):
            command = message.content.split(" ", 2)
            if command[0] == "!add":
                if command[1] == "help":
                    await message.channel.send("Syntax for !add\n"
                                                   + "```"
                                                   + "!add category name\n"
                                                   + "category: movie, animation, show, anime, cartoon\n"
                                                   + "name: name of the item you want to add\n"
                                                   + "```")

                if command[1] in trakt.lists and len(command) == 3:
                    res = trakt.add_to_list(command[1], command[2])
                    await message.channel.send(res)
                elif not command[1] in trakt.lists:
                    await message.channel.send("```\n"
                                               + f"{command[1]} category not in system"
                                               + "```")
        # await message.channel.send("toast")


intents = discord.Intents.default()
intents.message_content = True
# tmp = trakt.search("movie", "shrek")

client = MyClient(intents=intents)
client.run(token)
