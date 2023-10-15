from collections import Counter
from database import fetch_data_helpers
from database.db import async_db_executor, connect_to_db


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
