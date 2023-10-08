import pyodbc

DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server;',
    'server': 'LocalHost;',
    'database': 'discord_logs_db;',
    'trusted_connection': 'yes;'
}


def connect_to_db():
    cnxn = pyodbc.connect(**DATABASE_CONFIG)
    cursor = cnxn.cursor()
    return cnxn, cursor


def store_message_in_db(username, server, message, date):
    cnxn, cursor = connect_to_db()
    try:
        cursor.execute("INSERT INTO dbo.discord_logs_db (username, server, message, date) VALUES (?, ?, ?, ?)",
                       (username, server, message, date))
        cnxn.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")
    finally:
        cursor.close()
        cnxn.close()

