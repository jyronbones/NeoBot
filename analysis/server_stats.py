from discord import File
from analysis.user_growth import plot_user_growth
from configurations.config import days
from database.fetch_server_analysis_data import get_total_messages, get_total_links_shared, get_busiest_hour, \
    get_busiest_day, get_unique_users, get_avg_messages_per_user_async, get_user_growth_over_time, \
    get_messages_over_time
from database.fetch_server_users_analysis_data import get_message_with_mentions_count, get_top_users, \
    get_top_mentioners, get_active_channels, get_most_mentioned_users, get_oldest_users, \
    get_users_with_longest_messages, get_sentiment_leaders, get_sentiment_losers, get_users_with_most_links, \
    get_top_topic_starters


async def handle_serverstats(message):
    if message.guild is None:
        await message.channel.send("Sorry, I cannot fulfill this request in a DM 😞.")
        return

    server_name = message.guild.name

    # Total server stats
    total_messages = await get_total_messages(server_name)
    total_links = await get_total_links_shared(server_name)
    total_mentions = await get_message_with_mentions_count(server_name)
    busiest_hour = await get_busiest_hour(server_name)
    busiest_day = await get_busiest_day(server_name)
    unique_users = await get_unique_users(server_name)
    avg_messages_per_user = await get_avg_messages_per_user_async(server_name)
    daily_messages_over_time = await get_messages_over_time(server_name, "daily")
    weekly_messages_over_time = await get_messages_over_time(server_name, "weekly")
    yearly_messages_over_time = await get_messages_over_time(server_name, "yearly")

    user_growth_data = await get_user_growth_over_time(server_name)

    # Top user stats by server
    top_users_data = await get_top_users(server_name)
    top_mentions_data = await get_top_mentioners(server_name)
    active_channels_data = await get_active_channels(server_name)
    most_mentioned_users = await get_most_mentioned_users(server_name)
    oldest_users_data = await get_oldest_users(server_name)
    longest_messages_users_data = await get_users_with_longest_messages(server_name)
    sentiment_leaders_data = await get_sentiment_leaders(server_name)
    sentiment_losers_data = await get_sentiment_losers(server_name)
    users_with_most_links_data = await get_users_with_most_links(server_name)
    top_topic_starters_data = await get_top_topic_starters(server_name)

    # Getting the saved image path
    image_path = plot_user_growth(user_growth_data)

    # Server-wide statistics
    server_stats_message = f":bar_chart: **Server Statistics for {server_name}**\n"
    server_stats_message += f"\n:envelope: **Total Messages**: {total_messages}"
    server_stats_message += f"\n:link: **Total Links Shared**: {total_links}"
    server_stats_message += f"\n:loudspeaker: **Messages with Mentions**: {total_mentions}"

    if busiest_hour is not None:
        server_stats_message += f"\n⏰ **Busiest Time of Day**: {busiest_hour}:00 - {busiest_hour + 1}:00"
    else:
        server_stats_message += "\n⏰ **Busiest Time of Day**: Data not available"

    server_stats_message += f"\n📅 **Busiest Day of the Week**: {days[busiest_day[0]]}"
    server_stats_message += f"\n👥 **Number of Unique Users**: {unique_users}"
    server_stats_message += f"\n📩 **Average Messages per User**: {avg_messages_per_user:.2f}"

    # Calculate the total messages over the specified periods
    daily_total = sum([date_count[1] for date_count in daily_messages_over_time[:1]])
    weekly_total = sum([date_count[1] for date_count in weekly_messages_over_time[:7]])
    monthly_total = sum([date_count[1] for date_count in daily_messages_over_time[:30]])
    yearly_total = sum([date_count[1] for date_count in yearly_messages_over_time[:1]])

    server_stats_message += "\n📆 **Server Messages Over Time**:\n"
    server_stats_message += f"\t\t\t\t\t\t**Daily Messages:** {daily_total}\n"
    server_stats_message += f"\t\t\t\t\t\t**Weekly Messages:** {weekly_total}\n"
    server_stats_message += f"\t\t\t\t\t\t**Monthly Messages:** {monthly_total}\n"
    server_stats_message += f"\t\t\t\t\t\t**Yearly Messages:** {yearly_total}\n"

    server_stats_message += "\n:loud_sound: **Top 3 Active Channels**:\n"
    for i, channel in enumerate(active_channels_data, 1):
        server_stats_message += f"{i}. :speech_balloon: {channel[0]} - {channel[1]} messages\n"

    await message.channel.send(server_stats_message)

    # Sending the user growth image in Discord
    image = File(image_path, filename="images/user_growth.png")
    await message.channel.send("📈 **User Growth Over Time**", file=image)

    # Server Olympics - User Specific Stats
    user_stats_message = f"\n\n\n:trophy: **Server Olympics for {server_name}**:trophy:\n"

    # Format user statistics
    user_stats_message += "\n:trophy: **Top 3 Active Users**:\n"
    for i, user in enumerate(top_users_data, 1):
        user_stats_message += f"{i}. :bust_in_silhouette: {user[0]} - {user[1]} messages\n"

    user_stats_message += "\n:star2: **Top 3 Mentioners**:\n"
    for i, mention in enumerate(top_mentions_data, 1):
        user_stats_message += f"{i}. :busts_in_silhouette: {mention[0]} - {mention[1]} times\n"

    user_stats_message += "\n🏆 **Top 3 Most Mentioned Users**:\n"
    for i, user in enumerate(most_mentioned_users, 1):
        user_stats_message += f"{i}. 📣 {user[0]} - {user[1]} mentions\n"

    user_stats_message += "\n👴 **Top 3 Oldest Discord Users**:\n"
    for i, user in enumerate(oldest_users_data, 1):
        user_stats_message += f"{i}. :bust_in_silhouette: {user[0]}\n"

    user_stats_message += "\n🖊 **Top 3 Users with Longest Average Messages**:\n"
    for i, user in enumerate(longest_messages_users_data, 1):
        user_stats_message += f"{i}. :bust_in_silhouette: {user[0]} - Avg. {user[1]:.2f} characters per message\n"

    user_stats_message += "\n:heart: **Top 3 Vibe Check Champs**:\n"
    for i, user in enumerate(sentiment_leaders_data, 1):
        user_stats_message += f"{i}. :bust_in_silhouette: {user[0]} - Score: {user[1]:.2f}\n"

    user_stats_message += "\n:sob: **Top 3 Loser Vibes**:\n"
    for i, user in enumerate(sentiment_losers_data, 1):
        user_stats_message += f"{i}. :bust_in_silhouette: {user[0]} - Score: {user[1]:.2f}\n"

    user_stats_message += "\n🔗 **Top 3 Link Sharers & Their Top Domain**:\n"
    for i, user_data in enumerate(users_with_most_links_data, 1):
        user, total_links, most_common_domain, _ = user_data  # Using '_' to discard the domain_count
        user_stats_message += (f"{i}. :bust_in_silhouette: {user} - {total_links} links "
                               f"(Most Popular: {most_common_domain})\n")

    user_stats_message += "\n🎙 **Top {limit} Topic Starters**:\n".format(limit=len(top_topic_starters_data))
    for i, user in enumerate(top_topic_starters_data, 1):
        user_stats_message += f"{i}. :bust_in_silhouette: {user[0]} - {user[1]} conversations started\n"

    await message.channel.send(user_stats_message)
