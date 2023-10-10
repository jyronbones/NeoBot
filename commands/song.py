import asyncio
import requests
from configurations import keys, config


async def handle_song(client, is_private, message):
    # Ask the user for the lyrics
    target = message.channel if not is_private else message.author
    await target.send("Please enter the lyrics:")

    # Wait for the user to respond with the lyrics
    try:
        lyrics_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and not m.content.startswith(config.prefix)
        )
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter the lyrics!")
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
        await target.send(f"An error occurred: {e}")
        return

    # Send the song information to the user
    song_data = f"Song: {track_name}\nArtist: {artist_name}"
    await target.send(song_data)
