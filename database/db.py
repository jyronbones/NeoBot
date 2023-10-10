import pyodbc
from configurations import keys

DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': keys.DB_SERVER_NAME,
    'database': keys.DISCORD_LOGS_DB,
    'trusted_connection': 'yes'
}


def connect_to_db():
    cnxn = pyodbc.connect(**DATABASE_CONFIG)
    cursor = cnxn.cursor()
    return cnxn, cursor


def store_message_data(username, server, message, channel, date):
    username = username.split('#')[0]

    try:
        store_message_in_db(username, server, message, channel, date)
    except Exception as e:
        print(f"Failed to store message data: {e}")


def store_message_in_db(username, servername, channel, message, timestamp):
    cnxn, cursor = connect_to_db()
    try:
        cursor.execute("INSERT INTO dbo.discord_logs (username, servername, channel, message, timestamp) VALUES (?, "
                       "?, ?, ?, ?)",
                       (username, servername, channel, message, timestamp))
        cnxn.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")
    finally:
        cursor.close()
        cnxn.close()
