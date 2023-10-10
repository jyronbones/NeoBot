import asyncio
from configurations import config
from datetime import datetime
from analysis.word_cloud import create_word_cloud
from commands.catfact import handle_catfact
from commands.commands import commands
from commands.define import handle_define
from commands.help_commands import handle_commands
from commands.insult import handle_insult
from commands.news import handle_news
from commands.poem import handle_poem
from commands.question import handle_question
from commands.recipe import handle_recipe
from commands.reddit import handle_reddit
from commands.roll import handle_roll
from commands.song import handle_song
from commands.stock import handle_stock
from commands.trivia import handle_trivia
from commands.weather import handle_weather
from database.db import store_message_data
from commands.joke import handle_joke
from commands.movie import handle_movie
from commands.lyrics import handle_lyrics


async def on_ready():
    print(f"NeoBot logged in!")


async def on_message(client, message):
    if message.author == client.user:
        return

    if message.guild is not None:
        print(f"{message.author} in server '{message.guild.name}' ({message.channel.name}): {message.content}")
        store_message_data(str(message.author), str(message.guild.name), str(message.channel.name), message.content,
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print(f"{message.author} sent a private message: {message.content}")

    if message.content.startswith(config.prefix):
        is_private = False
        if message.content.startswith(f"{config.prefix}%"):
            is_private = True
            command = message.content[len(config.prefix) + 1:].strip()
        else:
            command = message.content[len(config.prefix):].strip()

        if command == "question":
            target = message.channel if not is_private else message.author
            await target.send("Please ask me a question!")

            try:
                question_message = await client.wait_for(
                    "message",
                    timeout=config.USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        config.prefix)
                )
            except asyncio.TimeoutError:
                timeout_message = "Sorry, you took too long to ask a question!"
                await target.send(timeout_message)
                return

            await handle_question(question_message, target)

        elif command == "roll":
            await handle_roll(is_private, message)

        elif command == "catfact":
            await handle_catfact(is_private, message)

        elif command == "weather":
            await handle_weather(client, is_private, message)

        elif command == "joke":
            await handle_joke(is_private, message)

        elif command == "movie":
            await handle_movie(is_private, message)

        elif command == "define":
            await handle_define(client, is_private, message)

        elif command == "reddit":
            await handle_reddit(client, is_private, message)

        elif command == "trivia":
            await handle_trivia(client, is_private, message)

        elif command == "news":
            await handle_news(client, is_private, message)

        elif command == "stock":
            await handle_stock(client, is_private, message)

        elif command == "song":
            await handle_song(client, is_private, message)

        elif command == "recipe":
            await handle_recipe(client, is_private, message)

        elif command == "poem":
            await handle_poem(is_private, message)

        elif command == "lyrics":
            await handle_lyrics(is_private, client, message)

        elif command == "insult":
            await handle_insult(client, is_private, message)

        elif command == "wordcloud":
            server = message.guild
            channel = message.channel
            await create_word_cloud(server, channel, is_private)

        elif command == "commands":
            await handle_commands(commands, config.prefix, message, is_private)
