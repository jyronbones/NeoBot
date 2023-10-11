import asyncio
import requests
from configurations import config
from utilities import keys


async def handle_weather(client, is_private, message):
    # Send a prompt asking the user to enter a location
    target = message.channel if not is_private else message.author
    await target.send("Please enter a location!")

    # Wait for the user to respond with a location
    try:
        location_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                config.prefix)
        )

    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter a location!")
        return

    # Make a request to the Weatherstack API to get the weather information
    params = {
        "access_key": keys.YOUR_WEATHERSTACK_API_KEY,
        "query": location_message.content
    }

    response = requests.get("http://api.weatherstack.com/current", params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            location = data["location"]["name"]
            temperature = data["current"]["temperature"]
            description = data["current"]["weather_descriptions"][0]

            await target.send(
                f"The weather in {location} is {description} with a temperature of {temperature} degrees Celsius.")
        except KeyError:
            await target.send(f"Sorry, I couldn't find weather information for the location: {location_message.content}.")
    else:
        await target.send("An error occurred while fetching the weather information.")
