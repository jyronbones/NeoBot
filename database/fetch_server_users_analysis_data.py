from collections import Counter, defaultdict
from urllib.parse import urlparse

from database import fetch_data_helpers
from database.db import async_db_executor, connect_to_db
from database.fetch_data_helpers import calculate_sentiment


async def get_top_users(servername, limit=3):
    return await async_db_executor(_get_top_users, servername, limit)


def _get_top_users(servername, limit):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        "SELECT TOP (?) username, COUNT(*) as count FROM dbo.discord_logs WHERE servername = ? GROUP BY username "
        "ORDER BY count DESC",
        (limit, servername)
    )
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


async def get_top_mentioners(servername, limit=3):
    return await async_db_executor(_get_top_mentioners, servername, limit)


def _get_top_mentioners(servername, limit):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        "SELECT TOP (?) username, COUNT(mentions) as count FROM dbo.discord_logs WHERE servername = ? AND mentions IS "
        "NOT NULL AND mentions <> '' GROUP BY username ORDER BY count DESC",
        (limit, servername)
    )
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


async def get_active_channels(servername, limit=3):
    return await async_db_executor(_get_active_channels, servername, limit)


def _get_active_channels(servername, limit):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        "SELECT TOP (?) channel, COUNT(*) as count FROM dbo.discord_logs WHERE servername = ? GROUP BY channel ORDER "
        "BY count DESC",
        (limit, servername)
    )
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


async def get_most_mentioned_users(servername, limit=3):
    return await async_db_executor(_get_most_mentioned_users, servername, limit)


def _get_most_mentioned_users(servername, limit):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT mentions
        FROM dbo.discord_logs 
        WHERE servername = ? AND mentions IS NOT NULL AND mentions <> ''
        """,
        (servername,)
    )

    rows = cursor.fetchall()
    cursor.close()
    cnxn.close()

    mentions = []
    for row in rows:
        mentions_in_row = row[0].split(',')
        mentions.extend(mentions_in_row)

    # Convert mentions to usernames
    mention_usernames = [fetch_data_helpers.fetch_username(mention) for mention in mentions if mention]
    mention_counts = Counter(mention_usernames)
    return mention_counts.most_common(limit)


async def get_message_with_mentions_count(servername):
    return await async_db_executor(_get_message_with_mentions_count, servername)


def _get_message_with_mentions_count(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM dbo.discord_logs WHERE servername = ? AND mentions IS NOT NULL AND mentions "
                   "<> ''", (servername,))
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


async def get_oldest_users(servername, limit=3):
    return await async_db_executor(_get_oldest_users, servername, limit)


def _get_oldest_users(servername, limit):
    cnxn, cursor = connect_to_db()
    query = """
        SELECT TOP (?) username, userid
        FROM (
            SELECT DISTINCT username, userid
            FROM dbo.discord_logs
            WHERE servername = ? AND ISNUMERIC(userid) = 1
        ) AS subquery
        ORDER BY CAST(userid AS BIGINT)
    """
    cursor.execute(query, (limit, servername))
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


# Top 3 Users with the Longest Messages
async def get_users_with_longest_messages(servername, limit=3):
    return await async_db_executor(_get_users_with_longest_messages, servername, limit)


def _get_users_with_longest_messages(servername, limit):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT TOP (?) username, AVG(LEN(message)) as avg_length 
        FROM dbo.discord_logs 
        WHERE servername = ?
        GROUP BY username 
        ORDER BY avg_length DESC
        """,
        (limit, servername)
    )
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


async def get_sentiment_leaders(servername, limit=3):
    return await async_db_executor(_get_sorted_sentiments_desc, servername, limit)


async def get_sentiment_losers(servername, limit=3):
    return await async_db_executor(_get_sorted_sentiments_asc, servername, limit)


def _get_sorted_sentiments_desc(servername, limit):
    return _get_sorted_sentiments(servername, limit, "desc")


def _get_sorted_sentiments_asc(servername, limit):
    return _get_sorted_sentiments(servername, limit, "asc")


def _get_sorted_sentiments(servername, limit, order):
    cnxn, cursor = connect_to_db()

    cursor.execute(
        """
        SELECT username, message
        FROM dbo.discord_logs
        WHERE servername = ?
        """,
        (servername,)
    )

    rows = cursor.fetchall()

    # Calculate sentiment for each message and store
    user_sentiments = {}
    for row in rows:
        username = row[0]
        message = row[1]
        sentiment = calculate_sentiment(message)

        if username in user_sentiments:
            user_sentiments[username].append(sentiment)
        else:
            user_sentiments[username] = [sentiment]

    # Calculate average sentiment for each user
    avg_sentiments = {}
    for user, sentiments in user_sentiments.items():
        avg_sentiments[user] = sum(sentiments) / len(sentiments)

    # Sort users by average sentiment
    if order == "desc":
        sorted_users = sorted(avg_sentiments.items(), key=lambda x: x[1], reverse=True)
    else:  # 'asc' or any other value will default to ascending order
        sorted_users = sorted(avg_sentiments.items(), key=lambda x: x[1])

    cursor.close()
    cnxn.close()

    # Return users based on sentiment
    return sorted_users[:limit]


async def get_users_with_most_links(servername, limit=3):
    return await async_db_executor(_get_users_with_most_links, servername, limit)


def _get_users_with_most_links(servername, limit):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT username, links
        FROM dbo.discord_logs
        WHERE servername = ? AND links IS NOT NULL AND links <> ''
        """,
        (servername,)
    )

    rows = cursor.fetchall()

    # Create a dictionary to hold user data
    user_link_data = defaultdict(Counter)

    # Iterate through each row to extract links and then the domain of each link
    for row in rows:
        username = row[0]
        links = row[1].split(',')

        # Extract the domain from each link and increment the count
        for link in links:
            domain = urlparse(link).netloc
            user_link_data[username][domain] += 1

    cursor.close()
    cnxn.close()

    # Sort users based on the total number of links they shared
    sorted_users = sorted(user_link_data.items(), key=lambda x: sum(x[1].values()), reverse=True)

    # Modify the output to include the most popular domain for each user
    top_users = []
    for user, domains in sorted_users[:limit]:
        # This gives us the most common domain for the user
        most_common_domain, domain_count = domains.most_common(1)[0]

        total_links = sum(domains.values())
        top_users.append((user, total_links, most_common_domain, domain_count))

    return top_users


async def get_top_topic_starters(servername, limit=3, time_frame_minutes=10):
    return await async_db_executor(_get_top_topic_starters, servername, limit, time_frame_minutes)


def _get_top_topic_starters(servername, limit, time_frame_minutes):
    cnxn, cursor = connect_to_db()

    # A self-join query that counts the number of subsequent messages within the given time frame for each message
    query = """
    SELECT initiator.username, COUNT(follower.username) as conversation_count
    FROM dbo.discord_logs AS initiator
    JOIN dbo.discord_logs AS follower ON initiator.servername = follower.servername
                                      AND initiator.channel = follower.channel
                                      AND initiator.timestamp < follower.timestamp
                                      AND DATEADD(MINUTE, ?, initiator.timestamp) > follower.timestamp
                                      AND initiator.username <> follower.username
    WHERE initiator.servername = ?
    GROUP BY initiator.username
    ORDER BY conversation_count DESC
    """

    cursor.execute(query, (time_frame_minutes, servername))

    results = cursor.fetchmany(limit)

    cursor.close()
    cnxn.close()

    return results
