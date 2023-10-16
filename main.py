import asyncio
from configurations.config import client
from discord_bot import events
from utilities import keys


@client.event
async def on_ready():
    await events.on_ready(client)


@client.event
async def on_message(message):
    await events.on_message(client, message)

if __name__ == "__main__":
    try:
        asyncio.run(client.start(keys.DISCORD_BOT_TOKEN))
    except KeyboardInterrupt:
        print("Bot shutting down...")
        asyncio.run(client.close())
        print("Bot is now offline.")
