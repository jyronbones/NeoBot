import pyodbc
from database.db import connect_to_db
from database.message_extractors import extract_user_id_from_mention
from textblob import TextBlob


def fetch_username(discord_userid):
    """Fetch the username associated with a user ID"""
    if not discord_userid:
        raise ValueError("Invalid user mention provided")

    cnxn, cursor = None, None
    try:
        cnxn, cursor = connect_to_db()

        user_id = extract_user_id_from_mention(discord_userid)
        if not user_id:
            raise ValueError("Invalid mention format")

        query = """
        SELECT DISTINCT(username) 
        FROM dbo.discord_logs 
        WHERE userid=?
        """

        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return 'No data'  # Return a default value if no result is found

    except pyodbc.Error as e:
        print(f"Database error occurred: {e}")
        raise RuntimeError(f"Failed to fetch username for mention: {discord_userid}") from e

    finally:
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()


def calculate_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity
