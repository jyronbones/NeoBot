import asyncio
import pyodbc
from collections import Counter
from utilities import keys
from database.message_extractors import extract_mentions, extract_links

DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': keys.DB_SERVER_NAME,
    'database': keys.DISCORD_LOGS_DB,
    'trusted_connection': 'yes'
}

loop = asyncio.get_event_loop()


def connect_to_db():
    cnxn = pyodbc.connect(**DATABASE_CONFIG)
    cursor = cnxn.cursor()
    return cnxn, cursor


async def store_message_data(username, user_id, server, channel, message, date):
    username = username.split('#')[0]
    mentions = extract_mentions(message)
    links = extract_links(message)

    current_loop = asyncio.get_running_loop()  # Get the currently running loop

    try:
        await current_loop.run_in_executor(
            None, store_message_in_db, username, user_id, server, channel, message, date, mentions, links)
    except Exception as e:
        print(f"Failed to store message data: {e}")


def store_message_in_db(username, user_id, servername, channel, message, timestamp, mentions, links):
    cnxn, cursor = connect_to_db()
    try:
        mentions_str = ','.join(mentions)
        links_str = ','.join(links)
        cursor.execute("INSERT INTO dbo.discord_logs (username, userid, servername, channel, message, timestamp, "
                       "mentions, links) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (username, user_id, servername, channel,
                                                                            message, timestamp, mentions_str,
                                                                            links_str))
        cnxn.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")
    finally:
        cursor.close()
        cnxn.close()


def get_total_messages(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM dbo.discord_logs WHERE servername = ?", (servername,))
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


def get_top_users(servername, limit=3):
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


def get_total_links_shared(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM dbo.discord_logs WHERE servername = ? AND links IS NOT NULL AND links <> ''",
                   (servername,))
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


def get_top_mentioners(servername, limit=3):
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


def get_active_channels(servername, limit=3):
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


def get_messages_over_time(servername, interval="daily"):
    cnxn, cursor = connect_to_db()
    if interval == "daily":
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy-MM-dd') as date, COUNT(*) as count FROM dbo.discord_logs WHERE "
                       "servername = ? GROUP BY FORMAT(timestamp, 'yyyy-MM-dd') ORDER BY date DESC", (servername,))
    elif interval == "weekly":
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy-MM-dd', 'en-US') as date, COUNT(*) as count FROM "
                       "dbo.discord_logs WHERE servername = ? GROUP BY DATEPART(week, timestamp) ORDER BY date DESC",
                       (servername,))
    elif interval == "monthly":
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy-MM') as date, COUNT(*) as count FROM dbo.discord_logs WHERE "
                       "servername = ? GROUP BY FORMAT(timestamp, 'yyyy-MM') ORDER BY date DESC", (servername,))
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


def get_message_with_mentions_count(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM dbo.discord_logs WHERE servername = ? AND mentions IS NOT NULL AND mentions "
                   "<> ''", (servername,))
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


def get_most_mentioned_users(servername, limit=3):
    from database import fetch_data

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
    mention_usernames = [fetch_data.fetch_username(mention) for mention in mentions if mention]
    mention_counts = Counter(mention_usernames)
    return mention_counts.most_common(limit)


def get_busiest_hour(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT DATEPART(HOUR, timestamp) as hour, COUNT(*) as count 
        FROM dbo.discord_logs 
        WHERE servername = ? 
        GROUP BY DATEPART(HOUR, timestamp) 
        ORDER BY count DESC 
        """,
        (servername,)
    )
    results = cursor.fetchone()
    cursor.close()
    cnxn.close()
    return results


def get_busiest_day(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT DATEPART(WEEKDAY, timestamp) as day, COUNT(*) as count 
        FROM dbo.discord_logs 
        WHERE servername = ? 
        GROUP BY DATEPART(WEEKDAY, timestamp) 
        ORDER BY count DESC 
        """,
        (servername,)
    )
    results = cursor.fetchone()
    cursor.close()
    cnxn.close()
    return results


def get_unique_users(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT COUNT(DISTINCT username) 
        FROM dbo.discord_logs 
        WHERE servername = ?
        """,
        (servername,)
    )
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


def get_avg_messages_per_user(servername):
    total_messages = get_total_messages(servername)
    unique_users = get_unique_users(servername)
    return total_messages / unique_users if unique_users != 0 else 0


def get_user_growth_over_time(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT FORMAT(timestamp, 'yyyy-MM-dd') as date, COUNT(DISTINCT username) as new_users
        FROM dbo.discord_logs 
        WHERE servername = ? 
        GROUP BY FORMAT(timestamp, 'yyyy-MM-dd') 
        ORDER BY date ASC
        """,
        (servername,)
    )
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


def get_oldest_users(servername, limit=3):
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

