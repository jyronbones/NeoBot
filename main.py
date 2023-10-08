from datetime import datetime
import html
import time
import discord
import requests
import openai
import asyncio
import random
from commands import commands
import keys
from db import store_message_data

client = discord.Client(intents=discord.Intents.all())

# Define the prefix for the bot commands
prefix = "!"

# Define timeout time for user response
USER_RESPONSE_TIME = 120.0

# Define the Open Trivia DB API endpoint and default parameters
trivia_api_url = 'https://opentdb.com/api.php'
trivia_params = {
    'amount': 1,  # Get only one question
    'type': 'multiple',  # Get only multiple choice questions
}


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.guild is not None:
        print(f"{message.author} in server '{message.guild.name}' ({message.channel.name}): {message.content}")
        store_message_data(str(message.author), str(message.guild.name), str(message.channel.name), message.content,
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print(f"{message.author} sent a private message: {message.content}")

    if message.content.startswith(prefix):
        is_private = False
        if message.content.startswith(f"{prefix}%"):
            is_private = True
            command = message.content[len(prefix) + 1:].strip()
        else:
            command = message.content[len(prefix):].strip()

        if command == "question":
            # Send a prompt asking the user to ask a question
            target = message.channel if not is_private else message.author
            await target.send("Please ask me a question!")

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
                timeout_message = "Sorry, you took too long to ask a question!"
                await target.send(timeout_message)
                return

            max_retries = 5
            retry_count = 0

            while retry_count < max_retries:
                try:
                    response = openai.ChatCompletion.create(
                        model=keys.MODEL_ENGINE,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": (question_message.content + "(You must keep your response "
                                                                                    "under 2000 characters.")},
                        ]
                    )
                    await target.send(response['choices'][0]['message']['content'])
                    break
                except openai.error.RateLimitError:
                    wait_time = (2 ** retry_count) + 1
                    time.sleep(wait_time)
                    retry_count += 1
                except openai.error.OpenAIError as e:
                    error_message = f"Encountered an error while processing your request: {e}"
                    await target.send(error_message)
                    break
                except Exception as e:
                    error_message = f"An unexpected error occurred: {e}"
                    await target.send(error_message)
                    break

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
                "access_key": keys.YOUR_WEATHERSTACK_API_KEY,
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

        elif command == "movie":
            # Get a list of popular movies from TMDb API
            url = "https://api.themoviedb.org/3/movie/popular"
            params = {
                "api_key": keys.TMDB_API_KEY,
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

        elif command == "define":
            # Send a prompt asking the user to enter a word to define
            if not is_private:
                await message.channel.send("Please enter a word to define!")
            else:
                await message.author.send("Please enter a word to define!")

            # Wait for the user to respond with a word to define
            try:
                word_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )

            except asyncio.TimeoutError:

                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a word!")
                else:
                    await message.author.send("Sorry, you took too long to enter a word!")

                return

            # Make a request to the Urban Dictionary API to get the definition
            response = requests.get(f"https://api.urbandictionary.com/v0/define?term={word_message.content}")

            if response.status_code == 200:
                data = response.json()
                if data["list"]:
                    # Get the first definition and example
                    definition = data["list"][0]["definition"]
                    example = data["list"][0]["example"]

                    # Send the definition and example to the same channel or in a private message
                    if not is_private:
                        await message.channel.send(f"**{word_message.content}**\n\n{definition}\n\nExample: {example}")
                    else:
                        await message.author.send(f"**{word_message.content}**\n\n{definition}\n\nExample: {example}")
                else:
                    # If no definitions were found, send a message indicating that
                    if not is_private:
                        await message.channel.send(f"No definitions were found for **{word_message.content}**.")
                    else:
                        await message.author.send(f"No definitions were found for **{word_message.content}**.")
            else:
                # If an error occurred, send a message indicating that
                if not is_private:
                    await message.channel.send("An error occurred while fetching the definition.")
                else:
                    await message.author.send("An error occurred while fetching the definition.")

        elif command == "reddit":
            # Ask the user for the subreddit and number of posts they want to retrieve
            if not is_private:
                await message.channel.send("What subreddit do you want to get posts from?")
            else:
                await message.author.send("What subreddit do you want to get posts from?")
            try:
                subreddit_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )
                subreddit = subreddit_message.content.strip()

                if not is_private:
                    await message.channel.send(f"How many posts do you want to get from {subreddit}? (Maximum: 10)")
                else:
                    await message.author.send(f"How many posts do you want to get from {subreddit}? (Maximum: 10)")
                try:
                    limit_message = await client.wait_for(
                        "message",
                        timeout=USER_RESPONSE_TIME,
                        check=lambda
                            m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                            prefix)
                    )
                    limit = limit_message.content.strip()

                    # Check if the number of posts is valid
                    if not limit.isdigit() or int(limit) < 1 or int(limit) > 10:
                        raise ValueError("You exceeded the number of posts.\nPlease enter a valid number of posts ("
                                         "1-10).\nTry your command again...")

                    # Send the HTTP request to the Reddit API and retrieve the data
                    try:
                        response = requests.get(
                            f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}",
                            headers={"User-Agent": "Discord Bot"},
                        )
                        response.raise_for_status()
                        data = response.json()

                        # Extract the post titles from the data
                        titles = [post["data"]["title"] for post in data["data"]["children"]]

                        # Send the post titles to the user
                        if not is_private:
                            await message.channel.send("\n".join(titles))
                        else:
                            await message.author.send("\n".join(titles))
                    except requests.exceptions.HTTPError:
                        if not is_private:
                            await message.channel.send(
                                f"The subreddit you requested, {subreddit}, does not exist. Please try again with a "
                                f"different subreddit.")
                        else:
                            await message.author.send(
                                f"The subreddit you requested, {subreddit}, does not exist. Please try again with a "
                                f"different subreddit.")
                except asyncio.TimeoutError:
                    if not is_private:
                        await message.channel.send("Sorry, you took too long to respond with the number of posts!")
                    else:
                        await message.author.send("Sorry, you took too long to respond with the number of posts!")
                except ValueError as e:
                    if not is_private:
                        await message.channel.send(str(e))
                    else:
                        await message.author.send(str(e))
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to respond with the subreddit!")
                else:
                    await message.author.send("Sorry, you took too long to respond with the subreddit!")
            except requests.exceptions.HTTPError as e:
                if not is_private:
                    await message.channel.send(f"An error occurred: {e}")
                else:
                    await message.author.send(f"An error occurred: {e}")

        if command == "trivia":
            # Fetch the trivia data
            response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
            data = response.json()["results"][0]

            # Send the question to the user
            question = f"**Category:** {data['category']}\n\n{data['question']}\n\n"

            # Add the answer choices
            choices = data['incorrect_answers'] + [data['correct_answer']]
            random.shuffle(choices)
            for i, choice in enumerate(choices):
                question += f"{i + 1}. {choice}\n"

            if not is_private:
                await message.channel.send(question + "\nPlease enter the number of the correct answer.")
            else:
                await message.author.send(question + "\nPlease enter the number of the correct answer.")

            # Wait for the user to respond with an answer
            try:
                answer_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and m.content.isdigit() and 1 <= int(
                        m.content) <= len(choices)
                )
                user_answer = int(answer_message.content) - 1
                correct_answer = choices.index(data['correct_answer'])
                if user_answer == correct_answer:
                    if not is_private:
                        await message.channel.send("Correct! :white_check_mark: \nYou answered correctly.")
                    else:
                        await message.author.send("Correct! :white_check_mark: \nYou answered correctly.")
                else:
                    if not is_private:
                        await message.channel.send(
                            f"Incorrect! :x: \nThe correct answer was **{data['correct_answer']}**.")
                    else:
                        await message.author.send(
                            f"Incorrect! :x: \nThe correct answer was **{data['correct_answer']}**.")
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to answer.")
                else:
                    await message.author.send("Sorry, you took too long to answer.")

        elif command == "news":
            news_api_url = "https://newsapi.org/v2/top-headlines"
            valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']

            # Get the user's preferred news category
            if not is_private:
                await message.channel.send("Please enter a news category \n(e.g., 'business', 'entertainment', "
                                           "'general', 'health', 'science', 'sports', 'technology'):")
            else:
                await message.author.send("Please enter a news category \n(e.g., 'business', 'entertainment', "
                                          "'general', 'health', 'science', 'sports', 'technology'):")
            try:
                category_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda m: m.author == message.author and not m.content.startswith(prefix)
                )
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a news category!")
                else:
                    await message.author.send("Sorry, you took too long to enter a news category!")
                return

            category = category_message.content.lower()

            if category not in valid_categories:
                if not is_private:
                    await message.channel.send(f"Sorry, {category} is not a valid news category. Please try your "
                                               f"command again")
                else:
                    await message.author.send(f"Sorry, {category} is not a valid news category. Please try your "
                                              f"command again")
                return

            # Get the news articles for the specified category
            try:
                response = requests.get(news_api_url,
                                        params={"category": category, "apiKey": keys.news_api_key, "language": "en"})
                response.raise_for_status()
                articles = response.json()["articles"]
            except (requests.exceptions.HTTPError, KeyError) as e:
                if not is_private:
                    await message.channel.send(f"An error occurred: {e}")
                else:
                    await message.author.send(f"An error occurred: {e}")
                return

            # Send the news articles to the user
            for article in articles:
                article_message = f"{article['title']}\n{article['url']}"
                if not is_private:
                    await message.channel.send(article_message)
                else:
                    await message.author.send(article_message)

        elif command == "stock":
            # Ask the user for the stock symbol
            if not is_private:
                await message.channel.send("Please enter a stock symbol (e.g., AAPL, GOOG):")
            else:
                await message.author.send("Please enter a stock symbol (e.g., AAPL, GOOG):")

            # Wait for the user to respond with the stock symbol
            try:
                stock_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda m: m.author == message.author and not m.content.startswith(prefix)
                )
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a stock symbol!")
                else:
                    await message.author.send("Sorry, you took too long to enter a stock symbol!")
                return

            # Use the Alpha Vantage API to get stock data for the specified symbol
            stock_symbol = stock_message.content.upper()
            api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={keys.ALPHA_VANTAGE_API_KEY}"
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()["Global Quote"]
            except (requests.exceptions.HTTPError, KeyError) as e:
                if not is_private:
                    await message.channel.send(f"An error occurred: {e}")
                else:
                    await message.author.send(f"An error occurred: {e}")
                return

            # Check if all fields are N/A
            if all(value == "N/A" for value in data.values()):
                if not is_private:
                    await message.channel.send(f"Stock data not found for symbol: {stock_symbol}")
                else:
                    await message.author.send(f"Stock data not found for symbol: {stock_symbol}")
                return

            # Format the stock data and send it to the user
            stock_data = f"Symbol: {data['01. symbol']}\nPrice: {data['05. price']}\nChange: {data['09. change']}\nPercent Change: {data['10. change percent']}"
            if not is_private:
                await message.channel.send(stock_data)
            else:
                await message.author.send(stock_data)

        elif command == "song":
            if not is_private:
                await message.channel.send("Please enter the lyrics:")
            else:
                await message.author.send("Please enter the lyrics:")

            # Wait for the user to respond with the lyrics
            try:
                lyrics_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda m: m.author == message.author and not m.content.startswith(prefix)
                )
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter the lyrics!")
                else:
                    await message.author.send("Sorry, you took too long to enter the lyrics!")
                return

            # Use the Musicmatch API to search for a song with the given lyrics
            lyrics = lyrics_message.content
            api_url = f"http://api.musixmatch.com/ws/1.1/track.search?q_lyrics={lyrics}&apikey={keys.MUSICMATCH_API_KEY}"
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                track_list = data["message"]["body"]["track_list"]
                if not track_list:
                    raise ValueError("No song found with the given lyrics.")
                track_name = track_list[0]["track"]["track_name"]
                artist_name = track_list[0]["track"]["artist_name"]
            except (requests.exceptions.HTTPError, KeyError, ValueError) as e:
                if not is_private:
                    await message.channel.send(f"An error occurred: {e}")
                else:
                    await message.author.send(f"An error occurred: {e}")
                return

            # Send the song information to the user
            song_data = f"Song: {track_name}\nArtist: {artist_name}"
            if not is_private:
                await message.channel.send(song_data)
            else:
                await message.author.send(song_data)

        elif command == "recipe":
            # Ask the user for the recipe they want to search for
            if not is_private:
                await message.channel.send("What recipe do you want to search for?")
            else:
                await message.author.send("What recipe do you want to search for?")

            # Wait for the user to respond with the recipe they want to search for
            try:
                recipe_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a recipe!")
                else:
                    await message.author.send("Sorry, you took too long to enter a recipe!")
                return
            food = recipe_message.content
            # Search for recipes using the Spoonacular API
            url = f"https://api.spoonacular.com/recipes/complexSearch?query={recipe_message.content}&apiKey={keys.SPOONACULAR_API_KEY}"
            try:
                response = requests.get(url).json()

                # Check if any recipes were found
                if response["results"]:
                    # Get the first recipe from the search results
                    recipe = response["results"][0]
                    recipe_name = recipe["title"]
                    recipe_id = recipe["id"]

                    # Get information about the recipe using the recipe ID
                    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={keys.SPOONACULAR_API_KEY}"
                    response = requests.get(url).json()

                    # Get the recipe instructions and ingredients
                    recipe_instructions = response["instructions"]
                    recipe_ingredients = response["extendedIngredients"]

                    # Format the recipe ingredients
                    formatted_ingredients = "\n".join(
                        [f"{ingredient['original']} ({ingredient['amount']} {ingredient['unit']})" for ingredient in
                         recipe_ingredients])

                    # Send the recipe information to the user
                    recipe_text = f"**{recipe_name}**\n\nIngredients:\n{formatted_ingredients}\n\nInstructions:\n{recipe_instructions}"
                    if not is_private:
                        await message.channel.send(recipe_text)
                    else:
                        await message.author.send(recipe_text)
                else:
                    if not is_private:
                        await message.channel.send("No recipes found!")
                    else:
                        await message.author.send("No recipes found!")
            except requests.exceptions.HTTPError as e:
                if not is_private:
                    await message.channel.send(f"{e}")
                else:
                    await message.author.send(f"{e}")
            except discord.errors.HTTPException as ee:
                if not is_private:
                    await message.channel.send(f"Sorry the recipe for {food} is too long (2000 word max)")
                else:
                    await message.channel.send(f"Sorry the recipe for {food} is too long (2000 word max)")

        elif command == "poem":
            # Get a random poem from the PoetryDB API
            try:
                response = requests.get("https://poetrydb.org/random")
                poem = response.json()[0]
                if not is_private:
                    await message.channel.send(
                        f"{poem['title']} by {poem['author']}:\n\n{poem['lines'][0]}\n{poem['lines'][1]}\n{poem['lines'][2]}")
                else:
                    await message.author.send(
                        f"{poem['title']} by {poem['author']}:\n\n{poem['lines'][0]}\n{poem['lines'][1]}\n{poem['lines'][2]}")
            except requests.exceptions.HTTPError as e:
                if not is_private:
                    await message.channel.send(f"{e}")
                else:
                    await message.author.send(f"{e}")

        elif command == "lyrics":
            # Send a prompt asking the user for a song name
            if not is_private:
                await message.channel.send("Please enter the name of a song:")
            else:
                await message.author.send("Please enter the name of a song:")

            # Wait for the user to respond with a song name
            try:
                song_name_message = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a song name!")
                else:
                    await message.author.send("Sorry, you took too long to enter a song name!")
                return

            # Get the lyrics of the song using the Musixmatch API
            try:
                url = f"https://api.musixmatch.com/ws/1.1/track.search?q_track={song_name_message.content}&page_size" \
                      f"=1&s_track_rating=desc&apikey={keys.MUSICMATCH_API_KEY}"
                response = requests.get(url)
                data = response.json()
                track_list = data["message"]["body"]["track_list"]
                if not track_list:
                    if not is_private:
                        await message.channel.send(
                            f"Sorry, I couldn't find the lyrics for {song_name_message.content}!")
                    else:
                        await message.author.send(f"Sorry, I couldn't find the lyrics for {song_name_message.content}!")
                    return
                track_id = track_list[0]["track"]["track_id"]
                url = f"https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}&apikey={keys.MUSICMATCH_API_KEY}"
                response = requests.get(url)
                data = response.json()
                lyrics = data["message"]["body"]["lyrics"]["lyrics_body"].replace(
                    "** This Lyrics is NOT for Commercial use **", "")
                if not is_private:
                    await message.channel.send(lyrics.strip())
                else:
                    await message.author.send(lyrics.strip())
            except requests.exceptions.HTTPError as e:
                if not is_private:
                    await message.channel.send(f"{e}")
                else:
                    await message.author.send(f"{e}")

        elif command == "insult":
            if not is_private:
                await message.channel.send("Who do you want me to insult?")
            else:
                await message.author.send("Who do you want me to insult?")

            try:
                response = await client.wait_for(
                    "message",
                    timeout=USER_RESPONSE_TIME,
                    check=lambda
                        m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                        prefix)
                )
                insultee = response.content
                if '<@1086521876156776548>' or 'neobot' in insultee.lower():
                    insultee = str(message.author).split("#", 1)[0]
                response = requests.get(
                    f"https://evilinsult.com/generate_insult.php?lang=en&type=json&insult={insultee}")
                data = response.json()
                insult = html.unescape(data["insult"])
                if not is_private:
                    await message.channel.send(insultee + ", " + insult)
                else:
                    await message.author.send(insult)
            except requests.exceptions.RequestException as e:
                if not is_private:
                    await message.channel.send(f"An error occurred: {e}")
                else:
                    await message.author.send(f"An error occurred: {e}")
            except asyncio.TimeoutError:
                if not is_private:
                    await message.channel.send("Sorry, you took too long to enter a name!")
                else:
                    await message.author.send("Sorry, you took too long to enter a name!")

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
client.run(keys.DISCORD_BOT_TOKEN)
