import requests
import asyncio
from configurations import config


async def handle_reddit(client, is_private, message):
    target = message.channel if not is_private else message.author

    await target.send("What subreddit do you want to get posts from?")

    subreddit = ""  # Define the subreddit variable here, outside the try block

    try:
        subreddit_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                config.prefix)
        )
        subreddit = subreddit_message.content.strip()

        await target.send(f"How many posts do you want to get from {subreddit}? (Maximum: 10)")

        limit_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and not m.content.startswith(
                config.prefix)
        )
        limit = limit_message.content.strip()

        if not limit.isdigit() or int(limit) < 1 or int(limit) > 10:
            raise ValueError(
                "You exceeded the number of posts.\nPlease enter a valid number of posts (1-10).\nTry your command again...")

        response = requests.get(
            f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}",
            headers={"User-Agent": "Discord Bot"},
        )
        response.raise_for_status()
        data = response.json()

        # Extract the post titles and their URLs from the data
        posts_info = [(post["data"]["title"], post["data"]["url"]) for post in data["data"]["children"]]

        # Format the titles with their URLs for output
        formatted_posts = [f"[{title}]({url})" for title, url in posts_info]

        await target.send("\n".join(formatted_posts))

    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to respond!")
    except ValueError as e:
        await target.send(str(e))
    except requests.exceptions.HTTPError:
        await target.send(
            f"The subreddit you requested, {subreddit}, does not exist. Please try again with a different subreddit.")
