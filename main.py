import discord
import json
import trakt_utils


class MyClient(discord.Client):
    async def on_message(self, message):
        if message.content.startswith("!add"):
            pass
        # await message.channel.send("toast")


with open('config.json') as f:
    data = json.load(f)
    token = data['discord_bot_token']


intents = discord.Intents.default()
intents.message_content = True

instance = trakt_utils.Trakt()
instance.login()

client = MyClient(intents=intents)
client.run(token)
