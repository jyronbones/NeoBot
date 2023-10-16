import asyncio
from analysis.server_stats import handle_serverstats
from configurations import config
from datetime import datetime
from analysis.word_cloud import create_word_cloud
from handlers.catfact import handle_catfact
from utilities.commands import commands
from handlers.define import handle_define
from handlers.help_commands import handle_commands
from handlers.insult import handle_insult
from handlers.news import handle_news
from handlers.poem import handle_poem
from handlers.question import handle_question
from handlers.recipe import handle_recipe
from handlers.reddit import handle_reddit
from handlers.roll import handle_roll
from handlers.song import handle_song
from handlers.stock import handle_stock
from handlers.trivia import handle_trivia
from handlers.weather import handle_weather
from database.db import store_message_data
from handlers.joke import handle_joke
from handlers.movie import handle_movie
from handlers.lyrics import handle_lyrics

is_answering_question = False


async def on_ready(client):
    print(f"👍 Login success as {client.user.name}!")


async def on_message(client, message):
    global is_answering_question

    if message.author == client.user:
        return

    if message.guild is not None:
        print(f"{message.author} in server '{message.guild.name}' ({message.channel.name}): {message.content}")
        await store_message_data(
            str(message.author),
            str(message.author.id),
            str(message.guild.name),
            str(message.channel.name),
            message.content,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    else:
        print(f"{message.author} sent a private message: {message.content}")

    if message.content.startswith(config.prefix):
        is_private = False
        if message.content.startswith(f"{config.prefix}%"):
            is_private = True
            command = message.content[len(config.prefix) + 1:].strip()
        else:
            command = message.content[len(config.prefix):].strip()

        if is_answering_question:
            await message.channel.send("I'm currently answering a question. Please wait.")
            return

        if command == "question":
            target = message.channel if not is_private else message.author
            await target.send("Please ask me a question!")

            try:
                is_answering_question = True
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
            is_answering_question = False

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
            await create_word_cloud(server.name, channel, is_private)

        elif command == "serverstats":
            await handle_serverstats(message)

        elif command == "commands":
            await handle_commands(commands, config.prefix, message, is_private)
