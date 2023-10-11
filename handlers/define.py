import asyncio
import requests
from configurations import config


async def handle_define(client, is_private, message):
    target = message.channel if not is_private else message.author
    await target.send("Please enter a word to define!")

    try:
        word_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                config.prefix)
        )
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter a word!")
        return

    response = requests.get(f"https://api.urbandictionary.com/v0/define?term={word_message.content}")
    if response.status_code == 200:
        data = response.json()
        if data["list"]:
            definition = data["list"][0]["definition"]
            example = data["list"][0]["example"]
            await target.send(f"**{word_message.content}**\n\n{definition}\n\nExample: {example}")
        else:
            await target.send(f"No definitions were found for **{word_message.content}**.")
    else:
        await target.send("An error occurred while fetching the definition.")
