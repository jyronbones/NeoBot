import os
import discord
import requests
from dotenv import load_dotenv
import openai
import asyncio
import random

load_dotenv()
client = discord.Client(intents=discord.Intents.all())

# Set up the OpenAI API credentials
model_engine = "text-davinci-002"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the prefix for the bot commands
prefix = "!"

# Define timeout time for user response
USER_RESPONSE_TIME = 60.0

# Define the commands and their descriptions
commands = {
    "question": "Ask the bot a question and get a response.",
    "roll": "Roll a random number between 1 and 6.",
    "weather": "Get the current weather for a location.",
    "movie": "Get a random movie recommendation.",
    "catfact": "Get a random cat fact.",
    "joke": "Get a random joke.",
    "commands": "Display a list of available commands.",
    "%'command'": "Command to receive a response privately."
}


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        is_private = False
        if message.content.startswith(f"{prefix}%"):
            is_private = True
            command = message.content[len(prefix) + 1:].strip()
        else:
            command = message.content[len(prefix):].strip()

        if command == "question":
            # Send a prompt asking the user to ask a question
            if not is_private:
                await message.channel.send("Please ask me a question!")
            else:
                await message.author.send("Please ask me a question!")

            # Wait for the user to respond with a question
            try:
                question_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to ask a question!")
                else:
                    await message.author.send("Sorry, you took too long to ask a question!")
                return

            # Get the response from OpenAI's GPT-3 model
            try:
                response = openai.Completion.create(
                    engine=model_engine,
                    prompt=question_message.content,
                    max_tokens=50
                )
                if not is_private:
                    await message.channel.send(response.choices[0].text.strip())
                else:
                    await message.author.send(response.choices[0].text.strip())
            except requests.exceptions.HTTPError as e:
                if not is_private:
                    await message.channel.send(f"An error occurred: {e}")
                else:
                    await message.author.send(f"An error occurred: {e}")

        elif command == "roll":
            # Roll a random number between 1 and 6
            random_number = random.randint(1, 6)

            # Send the result to the same channel or in a private message
            if not is_private:
                await message.channel.send(f"You rolled a {random_number}!")
            else:
                await message.author.send(f"You rolled a {random_number}!")

        elif command == "catfact":
            # Get a random cat fact from the catfact API
            response = requests.get("https://catfact.ninja/fact")
            if response.status_code == 200:
                catfact = response.json()["fact"]
                # Send the cat fact to the same channel or in a private message
                if not is_private:
                    await message.channel.send(catfact)
                else:
                    await message.author.send(catfact)
            else:
                if not is_private:
                    await message.channel.send("An error occurred while fetching the cat fact.")
                else:
                    await message.author.send("An error occurred while fetching the cat fact.")

        elif command == "weather":
            # Send a prompt asking the user to enter a location
            if not is_private:
                await message.channel.send("Please enter a location!")
            else:
                await message.author.send("Please enter a location!")

            # Wait for the user to respond with a location
            try:
                location_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )

            except asyncio.TimeoutError:

                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a location!")
                else:
                    await message.author.send("Sorry, you took too long to enter a location!")

                return

            # Make a request to the Weatherstack API to get the weather information
            params = {
                "access_key": os.getenv("YOUR_WEATHERSTACK_API_KEY"),
                "query": location_message.content
            }

            response = requests.get("http://api.weatherstack.com/current", params=params)
            if response.status_code == 200:
                data = response.json()
                location = data["location"]["name"]
                temperature = data["current"]["temperature"]
                description = data["current"]["weather_descriptions"][0]

                # Send the weather information to the same channel or in a private message
                if not is_private:
                    await message.channel.send(
                        f"The weather in {location} is {description} with a temperature of {temperature} degrees "
                        f"Celsius.")
                else:
                    await message.author.send(
                        f"The weather in {location} is {description} with a temperature of {temperature} degrees "
                        f"Celsius.")
            else:
                if not is_private:
                    await message.channel.send("An error occurred while fetching the weather information.")
                else:
                    await message.author.send("An error occurred while fetching the weather information.")

        elif command == "joke":
            # Get a random joke from the JokeAPI
            response = requests.get("https://v2.jokeapi.dev/joke/Any")
            if response.status_code == 200:
                # Parse the response JSON to get the joke
                joke_json = response.json()
                if joke_json["type"] == "twopart":
                    joke = f"{joke_json['setup']} {joke_json['delivery']}"
                else:
                    joke = joke_json["joke"]
                # Send the joke to the same channel or in a private message
                if not is_private:
                    await message.channel.send(joke)
                else:
                    await message.author.send(joke)
            else:
                if not is_private:
                    await message.channel.send("An error occurred while fetching the joke.")
                else:
                    await message.author.send("An error occurred while fetching the joke.")

        elif command == "gaydetector":
            if not is_private:
                sticker = discord.File('hazed.png', filename='hazed.png')
                await message.channel.send(file=sticker)
                await message.channel.send(f"This picture confirms Dom is truly gay.")
            else:
                sticker = discord.File('hazed.png', filename='hazed.png')
                await message.channel.send(file=sticker)
                await message.author.send(f"This picture confirms Dom is truly gay.")

        elif command == "movie":
            # Get a list of popular movies from TMDb API
            url = "https://api.themoviedb.org/3/movie/popular"
            params = {
                "api_key": os.getenv("TMDB_API_KEY"),
                "language": "en-US",
                "page": 1
            }
            response = requests.get(url, params=params)
            if response.status_code != 200:
                if not is_private:
                    await message.channel.send("An error occurred while fetching the movie information.")
                else:
                    await message.author.send("An error occurred while fetching the movie information.")
                return

            # Randomly recommend one of the movies
            results = response.json().get("results")
            if not results:
                if not is_private:
                    await message.channel.send("No movies found.")
                else:
                    await message.author.send("No movies found.")
                return

            recommended_movie = random.choice(results)
            title = recommended_movie.get("title")
            overview = recommended_movie.get("overview")
            if not is_private:
                await message.channel.send(f"I recommend watching {title}.\n{overview}")
            else:
                await message.author.send(f"I recommend watching {title}.\n{overview}")

        elif command == "commands":
            # Construct the list of commands and their descriptions
            command_list = "Available commands:\n```"
            for cmd, desc in commands.items():
                command_list += f"\n• {prefix}{cmd}: {desc}"

            command_list += "```"

            # Send the command list to the same channel or in a private message
            if not is_private:
                await message.channel.send(command_list)
            else:
                await message.author.send(command_list)


# Run the bot with your Discord bot token
client.run(os.getenv("DISCORD_TOKEN"))
