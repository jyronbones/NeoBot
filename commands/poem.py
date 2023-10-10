import requests


async def handle_poem(is_private, message):
    target = message.channel if not is_private else message.author

    try:
        response = requests.get("https://poetrydb.org/random")
        poem = response.json()[0]
        await target.send(
            f"{poem['title']} by {poem['author']}:\n\n{poem['lines'][0]}\n{poem['lines'][1]}\n{poem['lines'][2]}"
        )
    except requests.exceptions.HTTPError as e:
        await target.send(str(e))
    except Exception as e:
        await target.send(f"Sorry, an error occurred: {str(e)}")
