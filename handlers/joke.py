import requests


async def handle_joke(is_private, message):
    response = requests.get("https://v2.jokeapi.dev/joke/Any")

    target = message.channel if not is_private else message.author

    if response.status_code == 200:
        # Parse the response JSON to get the joke
        joke_json = response.json()
        if joke_json["type"] == "twopart":
            joke = f"{joke_json['setup']} {joke_json['delivery']}"
        else:
            joke = joke_json["joke"]

        await target.send(joke)

    else:
        await target.send("An error occurred while fetching the joke.")
