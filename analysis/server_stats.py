from discord import File
from analysis.user_growth import plot_user_growth
from configurations.config import days
from database.db import get_top_users, get_top_mentioners, get_active_channels, get_total_messages, \
    get_total_links_shared, get_message_with_mentions_count, get_most_mentioned_users, get_busiest_hour, \
    get_busiest_day, get_unique_users, get_avg_messages_per_user, get_user_growth_over_time, get_oldest_users


async def handle_serverstats(message):
    if message.guild is None:
        await message.channel.send("Sorry, I cannot fulfill this request in a DM 😞.")
        return

    server_name = message.guild.name
    top_users_data = get_top_users(server_name)
    top_mentions_data = get_top_mentioners(server_name)
    active_channels_data = get_active_channels(server_name)
    total_messages = get_total_messages(server_name)
    total_links = get_total_links_shared(server_name)
    total_mentions = get_message_with_mentions_count(server_name)
    most_mentioned_users = get_most_mentioned_users(server_name)
    oldest_users_data = get_oldest_users(server_name)
    busiest_hour = get_busiest_hour(server_name)
    busiest_day = get_busiest_day(server_name)
    unique_users = get_unique_users(server_name)
    avg_messages_per_user = get_avg_messages_per_user(server_name)
    user_growth_data = get_user_growth_over_time(server_name)

    # Getting the saved image path
    image_path = plot_user_growth(user_growth_data)

    # Format the fetched data into a message
    stats_message = f":bar_chart: **Server Statistics for {server_name}**\n"

    stats_message += f"\n:envelope: **Total Messages**: {total_messages}"
    stats_message += f"\n:link: **Total Links Shared**: {total_links}"
    stats_message += f"\n:loudspeaker: **Messages with Mentions**: {total_mentions}"
    stats_message += f"\n⏰ **Busiest Time of Day**: {busiest_hour[1]}:00 - {busiest_hour[1] + 1}:00 on {busiest_hour[0]}"
    stats_message += f"\n📅 **Busiest Day of the Week**: {days[busiest_day[0]]}"
    stats_message += f"\n👥 **Number of Unique Users**: {unique_users}"
    stats_message += f"\n📩 **Average Messages per User**: {avg_messages_per_user:.2f}"

    stats_message += "\n\n:trophy: **Top 3 Active Users**:\n"
    for i, user in enumerate(top_users_data, 1):
        stats_message += f"{i}. :bust_in_silhouette: {user[0]} - {user[1]} messages\n"

    stats_message += "\n\n:star2: **Top 3 Mentioners**:\n"
    for i, mention in enumerate(top_mentions_data, 1):
        stats_message += f"{i}. :busts_in_silhouette: {mention[0]} - {mention[1]} times\n"

    stats_message += "\n\n🏆 **Top 3 Most Mentioned Users**:\n"
    for i, user in enumerate(most_mentioned_users, 1):
        stats_message += f"{i}. 📣 {user[0]} - {user[1]} mentions\n"

    stats_message += "\n\n👴 **Top 3 Oldest Discord Users**:\n"
    for i, user in enumerate(oldest_users_data, 1):
        stats_message += f"{i}. :bust_in_silhouette: {user[0]}\n"

    stats_message += "\n\n:loud_sound: **Top 3 Active Channels**:\n"
    for i, channel in enumerate(active_channels_data, 1):
        stats_message += f"{i}. :speech_balloon: {channel[0]} - {channel[1]} messages\n"

    await message.channel.send(stats_message)

    # Sending the image in Discord
    image = File(image_path, filename="images/user_growth.png")
    await message.channel.send("📈 **User Growth Over Time**", file=image)
