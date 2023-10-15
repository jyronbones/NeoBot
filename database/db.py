import asyncio
import pyodbc
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


async def async_db_executor(func, *args):
    current_loop = asyncio.get_running_loop()
    return await current_loop.run_in_executor(None, func, *args)


async def store_message_data(username, user_id, server, channel, message, date):
    username = username.split('#')[0]
    mentions = extract_mentions(message)
    links = extract_links(message)
    await async_db_executor(store_message_in_db, username, user_id, server, channel, message, date, mentions, links)


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
