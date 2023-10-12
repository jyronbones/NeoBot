import pandas as pd
from utilities.commands import prefixed_commands
from database.db import connect_to_db
from utilities import keys


def fetch_data(servername):
    cnxn, cursor = connect_to_db()

    query = f"""
    SELECT message
    FROM {keys.DISCORD_LOGS_TABLE_NAME}
    WHERE servername=?
    """

    cursor.execute(query, (servername,))
    rows = cursor.fetchall()
    data = [row[0] for row in rows]

    cursor.close()
    cnxn.close()

    # Convert the data to a DataFrame
    df = pd.DataFrame(data, columns=['message'])

    # Filter out messages that match commands
    df = df[~df['message'].isin(prefixed_commands)]

    return df
