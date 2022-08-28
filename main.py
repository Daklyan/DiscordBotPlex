import json
import discord
import time
import datetime

from trakt_utils import Trakt
from discord import app_commands

with open('config.json') as f:
    data = json.load(f)
    token = data['discord_bot_token']
    channel_id = data['bot_channel_id']

current_timestamp = time.time()
trakt_logo_url = "https://trakt.tv/assets/logos/header@2x-d6926a2c93734bee72c5813819668ad494dbbda651457cd17d15d267bc75c657.png"

# Trakt
trakt = Trakt()
if not trakt.access_token:
    trakt.login()
elif(trakt.access_token and current_timestamp >= trakt.expire_date):
    trakt.refresh_login()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        #intents.message_content = True
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f'Logged as {self.user}')
        
        # Legacy way to handle command
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


client = MyClient()
tree = app_commands.CommandTree(client)

# Slash commands

# Commands list
@tree.command(name="commands")
async def self(interaction: discord.Interaction):
    embed_message = discord.Embed(title="Command list",
                                  description="Show available commands on this bot",
                                  timestamp=datetime.datetime.now(),
                                  color=discord.Colour.yellow())
    embed_message.add_field(name="commands", inline=True, value="List all commands available on this bot")
    
    # Empty fields
    embed_message.add_field(name="\u200B", value="\u200B", inline=True)
    embed_message.add_field(name="\u200B", value="\u200B", inline=True)
    
    embed_message.add_field(name="add", inline=True, value="Add an item to a trakt list\ncategory: trakt list name (available: anime, show, movie, animation, cartoon) you want to add to\nquery: name of the item you want to add")
    
    # Empty fields
    embed_message.add_field(name="\u200B", value="\u200B", inline=True)
    embed_message.add_field(name="\u200B", value="\u200B", inline=True)
    
    embed_message.add_field(name="remove", inline=True, value="Remove an item from a trakt list\ncategory: trakt list name (available: anime, show, movie, animation, cartoon) you want to remove from\nquery: name of the item you want to remove")
    await interaction.response.send_message(embed=embed_message)


# Add command
@tree.command(name="add", description="Add query item to Trakt list")
async def self(interaction: discord.Interaction, category: str, query: str):
    type = ""
    if category == 'movie' or category == 'animation':
        type = "movie"
    else:
        type = "show"
    if category in trakt.lists:
        res, trakt_url = trakt.add_to_list(category, query)
        if trakt_url:
            embed_message = discord.Embed(title=res[type]['title'],
                                          description=f'{res[type]["title"]} has been added to {trakt.lists[category]}',
                                          url=trakt_url,
                                          timestamp=datetime.datetime.now(),
                                          color=discord.Colour.green())
        else:
            embed_message = discord.Embed(title="Something's wrong I can feel it",
                                          description=res,
                                          timestamp=datetime.datetime.now(),
                                          color=discord.Colour.red())
        embed_message.set_author(name="Add item", icon_url=trakt_logo_url)
        await interaction.response.send_message(embed=embed_message)
    elif not category in trakt.lists:
        embed_message = discord.Embed(title="Something's wrong I can feel it",
                                      description=f'{category} category not found',
                                      timestamp=datetime.datetime.now(),
                                      color=discord.Colour.red())
        embed_message.set_author(name="Add item", icon_url=trakt_logo_url)
        await interaction.response.send_message(embed=embed_message)


# Remove command
@tree.command(name="remove", description="Remove item from Trakt list")
async def self(interaction: discord.Interaction, category: str, query:str):
    type = ""
    if category == 'movie' or category == 'animation':
        type = 'movie'
    else:
        type = 'show'

    if category in trakt.lists:
        res, trakt_url = trakt.remove_from_list(category, query)
        if trakt_url:
            embed_message = discord.Embed(title=res[type]['title'],
                                          description=f'{res[type]["title"]} has been removed from {trakt.lists[category]}',
                                          url=trakt_url,
                                          timestamp=datetime.datetime.now(),
                                          color=discord.Colour.green())
        else:
            embed_message = discord.Embed(title="Something's wrong I can feel it",
                                          description=res,
                                          timestamp=datetime.datetime.now(),
                                          color=discord.Colour.red())
        embed_message.set_author(name="Remove item", icon_url=trakt_logo_url)
        await interaction.response.send_message(embed=embed_message)
    elif not category in trakt.lists:
        embed_message = discord.Embed(title="Something's wrong I can feel it",
                                      description=f'{category} category was not found',
                                      timestamp=datetime.datetime.now(),
                                      color=discord.Colour.red())
        embed_message.set_author(name="Remove item", icon_url=trakt_logo_url)
        await interaction.response.send_message(embed=embed_message)

client.run(token)
