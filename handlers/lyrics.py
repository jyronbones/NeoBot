import requests
from configurations import config
from utilities import keys


async def handle_lyrics(is_private, client, message):
    # Define the target variable
    target = message.channel if not is_private else message.author

    await target.send("Please enter the name of a song:")

    try:
        song_name_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                config.prefix)
        )

        # Get the lyrics of the song using the Musixmatch API
        url = f"https://api.musixmatch.com/ws/1.1/track.search?q_track={song_name_message.content}&page_size=1" \
              f"&s_track_rating=desc&apikey={keys.MUSICMATCH_API_KEY}"
        response = requests.get(url)
        data = response.json()
        track_list = data["message"]["body"]["track_list"]

        if not track_list:
            await target.send(f"Sorry, I couldn't find the lyrics for {song_name_message.content}!")
            return

        track_id = track_list[0]["track"]["track_id"]
        url = f"https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}&apikey={keys.MUSICMATCH_API_KEY}"
        response = requests.get(url)
        data = response.json()
        lyrics = data["message"]["body"]["lyrics"]["lyrics_body"].replace("** This Lyrics is NOT for Commercial use **",
                                                                          "")
        await target.send(lyrics.strip())

    except requests.exceptions.HTTPError as e:
        await target.send(str(e))
