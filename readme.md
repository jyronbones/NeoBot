<h1>Neobot</h1>
Introducing a versatile Python Discord chatbot. Leveraging OpenAI GPT-4, it offers diverse responses, weather data, humor, and recommendations. Delivers stock updates, news, jokes, server statistics and much more.

<h2>Table of Contents</h2>
<ul>
  <li><a href="https://github.com/jyronbones/NeoBot#features">Features</a></li>
  <li><a href="https://github.com/jyronbones/NeoBot#prerequisites">Prerequisites</a></li>
  <li><a href="https://github.com/jyronbones/NeoBot#installation">Installation</a></li>
  <li><a href="https://github.com/jyronbones/NeoBot#usage">Usage</a></li>
  <li><a href="https://github.com/jyronbones/NeoBot#credits">Credits</a></li>


## Features
<ul>
<li>Returns a variety of information based on user requests</li>
<li>Uses OpenAI GPT-4 to answer user questions</li>
<li>Generates word clouds from server chat data</li>
<li>Provides weather data for specified locations</li>
<li>Returns random jokes and cat facts</li>
<li>Recommends movies and recipes based on user input</li>
<li>Can retrieve current stock data and recent news articles</li>
<li>Can generate server stats based on analysis from public user messages</li>
</ul>

## Prerequisites
Python 3.8+
Discord account
API keys for OpenAI, NewsAPI, Alpha Vantage, Music Match, and Spoonacular


## Installation
Clone the repository to your local machine
Install the required dependencies using pip:
<br>
```pip install -r requirements.txt```
<br><br>Create a .env file in the same directory as the bot.py file.
Add your API keys to the .env file:
```
DISCORD_BOT_TOKEN = <your discord bot token>
OPENAI_API_KEY = <your OpenAI API key>
NEWSAPI_KEY = <your NewsAPI key>
ALPHA_VANTAGE_API_KEY = <your Alpha Vantage API key>
MUSIC_MATCH_API_KEY = <your Music Match API key>
SPOONACULAR_API_KEY = <your Spoonacular API key>
YOUR_WEATHERSTACK_API_KEY = <your Weather Stack API key>
TMDB_API_KEY = <your TMDB API key>
DISCORD_LOGS_DB=<your DB name>
DISCORD_LOGS_TABLE_NAME=<your table name>
DB_SERVER_NAME=<your DB server name 'LocalHost'>
```
To run the bot, you will need to install the following Python packages:
<ul>
<li>discord
<li>requests
<li>dotenv
<li>openai
</ul>

Run the bot using:
<br>```python bot.py```
## Usage
-To use the bot, start by typing !commands to see a list of available commands.
<br>-To request information using the bot, type !<command> followed by the required parameters.
<br>-Some commands may require additional input from the user, in which case the bot will prompt the user to enter the required information.
<br>-If a command is preceded with %, the bot will respond privately to the user.

The bot supports the following commands:
<ul>
<li>%command: Command to receive a response privately.</li>
<li>catfact: Get a random cat fact.</li>
<li>wordcloud: Generate a word cloud from server chat data.</li>
<li>commands: Display a list of available commands.</li>
<li>define: Get a definition from Urban Dictionary.</li>
<li>joke: Get a random joke.</li>
<li>movie: Get a random movie recommendation.</li>
<li>news: Get recent news articles.</li>
<li>question: Ask the bot a question and get a response.</li>
<li>reddit: Get a specified number of the most recent posts (max 10) from a given subreddit.</li>
<li>roll: Roll a random number between 1 and 6.</li>
<li>song: Get a song title based on lyrics.</li>
<li>stock: Get current stock data.</li>
<li>recipe: Get recipe for a food.</li>
<li>trivia: Get a random trivia question</li>
<li>weather: Get the current weather for a location.</li>
<li>wordcloud: Generate a word cloud from server chat data.</li>
<li>serverstats: Display statistics about the server's activity.</li>
</ul>

## Credits
This bot was created by Byron Jones. It uses the following APIs:
<ul>
<li>OpenAI
<li>News API
<li>Alpha Vantage API
<li>Music Match API
<li>Spoonacular API
<li>WeatherStack API
<li>TMDB API
<li>Cat Fact API
<li>Open Trivia DB API
</ul>
</ul>
