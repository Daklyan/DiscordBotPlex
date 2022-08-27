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
                    embed_message = discord.Embed(title="Syntax for !add", 
                                                  description="!add category name\ncategory: movie, animation, show, anime, cartoon\nname: name of the item you want to add",
                                                  color=discord.Colour.yellow())
                    await message.channel.send(embed=embed_message)
                    return

                if command[1] in trakt.lists and len(command) == 3:
                    res, trakt_url = trakt.add_to_list(command[1], command[2])
                    if trakt_url:
                        embed_message = discord.Embed(title="Item added",
                                                      description=res,
                                                      url=trakt_url,
                                                      color=discord.Colour.green())
                    else:
                        embed_message = discord.Embed(title="Something wrong I can feel it",
                                                      description=res,
                                                      color=discord.Colour.red())
                    await message.channel.send(embed=embed_message)
                elif not command[1] in trakt.lists:
                    embed_message = discord.Embed(title="Error",
                                                  description=f"{command[1]} category not found",
                                                  color=discord.Colour.red())
                    await message.channel.send(embed=embed_message)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token)
