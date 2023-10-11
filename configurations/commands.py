commands = {
    "%'command'": "Command to receive a response privately.",
    "catfact": "Get a random cat fact.",
    "handlers": "Display a list of available commands.",
    "define": "Get a definition from Urban Dictionary.",
    "insult": "Insults a user.",
    "joke": "Get a random joke.",
    "lyrics": "Get lyrics of a song.",
    "movie": "Get a random movie recommendation.",
    "news": "Get recent news articles.",
    "poem": "Get a random poem.",
    "question": "Ask the bot a question and get a response.",
    "reddit": "Get a specified number of the most recent posts(max 10) from a given subreddit.",
    "roll": "Roll a random number between 1 and 6.",
    "song": "Get a song title based on lyrics.",
    "stock": "Get current stock data.",
    "recipe": "Get recipe for a food.",
    "trivia": "Get a random trivia question",
    "weather": "Get the current weather for a location.",
    "wordcloud": "Generate a word cloud from server chat data.",
    "serverstats": "Get an analysis of your server's activity."
}

prefixed_commands = ['!' + command for command in commands.keys()]
