import asyncio
import requests
from configurations import keys, config

valid_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']
news_api_url = "https://newsapi.org/v2/top-headlines"


async def handle_news(client, is_private, message):
    # Get the user's preferred news category
    target = message.channel if not is_private else message.author
    await target.send("Please enter a news category \n(e.g., 'business', 'entertainment', "
                      "'general', 'health', 'science', 'sports', 'technology'):")

    try:
        category_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and not m.content.startswith(config.prefix)
        )
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter a news category!")
        return

    category = category_message.content.lower()

    if category not in valid_categories:
        await target.send(f"Sorry, {category} is not a valid news category. Please try your command again.")
        return

    # Get the news articles for the specified category
    try:
        response = requests.get(news_api_url,
                                params={"category": category, "apiKey": keys.news_api_key, "language": "en"})
        response.raise_for_status()
        articles = response.json()["articles"]
    except (requests.exceptions.HTTPError, KeyError) as e:
        await target.send(f"An error occurred: {e}")
        return

    # Send the news articles to the user
    for article in articles:
        article_message = f"{article['title']}\n{article['url']}"
        await target.send(article_message)
