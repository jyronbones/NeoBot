import requests
import random
from utilities import keys


async def handle_movie(is_private, message):
    # Get a list of popular movies from TMDb API
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {
        "api_key": keys.TMDB_API_KEY,
        "language": "en-US",
        "page": 1
    }

    response = requests.get(url, params=params)
    target = message.channel if not is_private else message.author

    if response.status_code != 200:
        await target.send("An error occurred while fetching the movie information.")
        return

    # Randomly recommend one of the movies
    results = response.json().get("results")
    if not results:
        await target.send("No movies found.")
        return

    recommended_movie = random.choice(results)
    title = recommended_movie.get("title")
    overview = recommended_movie.get("overview")
    await target.send(f"I recommend watching {title}.\n{overview}")
