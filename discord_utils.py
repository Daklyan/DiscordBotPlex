import discord

class MyClient(discord.Client):
    async def on_message(self, message):
        if message.content.startswith("!add"):
            pass
        # await message.channel.send("toast")

