import asyncio
import requests
from configurations import config
from utilities import keys


async def handle_stock(client, is_private, message):
    # Ask the user for the stock symbol
    target = message.channel if not is_private else message.author
    await target.send("Please enter a stock symbol (e.g., AAPL, GOOG):")

    # Wait for the user to respond with the stock symbol
    try:
        stock_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and not m.content.startswith(config.prefix)
        )
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter a stock symbol!")
        return

    # Use the Alpha Vantage API to get stock data for the specified symbol
    stock_symbol = stock_message.content.upper()
    api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey={keys.ALPHA_VANTAGE_API_KEY}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()["Global Quote"]
    except (requests.exceptions.HTTPError, KeyError) as e:
        await target.send(f"An error occurred: {e}")
        return

    # Check if all fields are N/A
    if all(value == "N/A" for value in data.values()):
        await target.send(f"Stock data not found for symbol: {stock_symbol}")
        return

    # Format the stock data and send it to the user
    stock_data = f"Symbol: {data['01. symbol']}\nPrice: {data['05. price']}\nChange: {data['09. change']}\nPercent Change: {data['10. change percent']}"
    await target.send(stock_data)
