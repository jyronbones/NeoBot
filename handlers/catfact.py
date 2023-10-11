import requests


async def handle_catfact(is_private, message):
    # Get a random cat fact from the catfact API
    response = requests.get("https://catfact.ninja/fact")

    target = message.channel if not is_private else message.author

    if response.status_code == 200:
        catfact = response.json()["fact"]
        await target.send(catfact)
    else:
        await target.send("An error occurred while fetching the cat fact.")
