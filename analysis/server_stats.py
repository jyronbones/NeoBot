from database.fetch_users import fetch_top_users


async def handle_serverstats(message):
    server = message.guild
    top_users = fetch_top_users(server.name)

    stats_message = "**Server Statistics**\n"
    stats_message += "\n**Top 3 Active Users**:\n"
    for i, user in enumerate(top_users, 1):
        stats_message += f"{i}. {user['username']} - {user['message_count']} messages\n"

    await message.channel.send(stats_message)
