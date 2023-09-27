import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Define Discord bot token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# Set up the OpenAI API credentials
model_engine = "gpt-3.5-turbo"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define news API key
news_api_key = os.getenv("NEWSAPI_KEY")

# Define Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Define Music Match API key
MUSICMATCH_API_KEY = os.getenv("MUSIC_MATCH_API_KEY")

# Define Spoonacular API key
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

# Define Weather Stack API key
YOUR_WEATHERSTACK_API_KEY = os.getenv("YOUR_WEATHERSTACK_API_KEY")

# Define TMDB API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
