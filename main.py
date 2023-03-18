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

# Define the commands and their descriptions
commands = {
    "question": "Ask the bot a question and get a response.",
    "roll": "Roll a random number between 1 and 6.",
    "commands": "Display a list of available commands."
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
            command = message.content[len(prefix)+1:].strip()
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
                    timeout=30.0,
                    check=lambda m: m.author == message.author and m.channel == message.channel
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
