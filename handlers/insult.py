import requests
from configurations import config
import html
import asyncio


async def handle_insult(client, is_private, message):
    target = message.channel if not is_private else message.author

    await target.send("Who do you want me to insult?")

    try:
        response = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                config.prefix)
        )

        insultee = response.content
        if '<@1086521876156776548>' or 'neobot' in insultee.lower():
            insultee = str(message.author).split("#", 1)[0]

        api_response = requests.get(f"https://evilinsult.com/generate_insult.php?lang=en&type=json&insult={insultee}")
        data = api_response.json()
        insult = html.unescape(data["insult"])

        await target.send(insultee + ", " + insult)

    except requests.exceptions.RequestException as e:
        await target.send(f"An error occurred: {e}")
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter a name!")
