<h1>Discord Bot</h1>
This is a Python-based Discord chatbot that is designed to perform a number of tasks, such as providing trivia questions, getting stock data, and recommending movies or recipes.


## Features
Returns a variety of information based on user requests
<br>Uses OpenAI GPT-3 to answer user questions
Provides weather data for specified locations
Returns random jokes and cat facts
Recommends movies and recipes based on user input
Can retrieve current stock data and recent news articles

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
OPENAI_API_KEY = <your OpenAI API key>
NEWSAPI_KEY = <your NewsAPI key>
ALPHA_VANTAGE_API_KEY = <your Alpha Vantage API key>
MUSIC_MATCH_API_KEY = <your Music Match API key>
SPOONACULAR_API_KEY = <your Spoonacular API key>
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
To use the bot, start by typing !commands to see a list of available commands.
<br>To request information using the bot, type !<command> followed by the required parameters.
<br>Some commands may require additional input from the user, in which case the bot will prompt the user to enter the required information.
<br>If a command is preceded with %, the bot will respond privately to the user.

The bot supports the following commands:
<ul>
<li>%command: Command to receive a response privately.
<li>catfact: Get a random cat fact.
<li>commands: Display a list of available commands.
<li>define: Get a definition from Urban Dictionary
<li>joke: Get a random joke.
<li>movie: Get a random movie recommendation.
<li>news: Get recent news articles.
<li>question: Ask the bot a question and get a response.
<li>reddit: Get a specified number of the most recent posts (max 10) from a given subreddit.
<li>roll: Roll a random number between 1 and 6.
<li>song: Get a song title based on lyrics.
<li>stock: Get current stock data.
<li>recipe: Get recipe for a food.
<li>trivia: Get a random trivia question
<li>weather: Get the current weather for a location.
</ul>

## Credits
This bot was created by Byron Jones. It uses the following APIs:
<ul>
<li>OpenAI
<li>News API
<li>Alpha Vantage
<li>Music Match
<li>Spoonacular
<li>Cat Fact API
<li>Open Trivia DB API
</ul>