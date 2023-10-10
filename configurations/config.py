import discord

# Define the prefix for the bot commands
prefix = "!"

# Define timeout time for user response
USER_RESPONSE_TIME = 120.0

# Initialize all possible Discord event types (intents) to be received by the bot
discord_intents = discord.Intents.all()
