import discord
from discord_bot import events
from configurations import keys
from configurations.config import discord_intents


client = discord.Client(intents=discord_intents)


@client.event
async def on_ready():
    await events.on_ready()


@client.event
async def on_message(message):
    await events.on_message(client, message)

if __name__ == "__main__":
    client.run(keys.DISCORD_BOT_TOKEN)
