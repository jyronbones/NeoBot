import asyncio
from concurrent.futures import ThreadPoolExecutor
import keys
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from database.db import connect_to_db

executor = ThreadPoolExecutor()


async def create_word_cloud(servername):
    loop = asyncio.get_event_loop()

    # Run the database operations in a separate thread
    df = await loop.run_in_executor(executor, fetch_data, servername)

    # Check if data is retrieved successfully
    if df.empty:
        print("No messages retrieved for the specified servername.")
        return

    # Generate and display word cloud
    text = ' '.join(df['message'])
    wordcloud = WordCloud(background_color='white').generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


def fetch_data(servername):
    cnxn, cursor = connect_to_db()

    query = f"""
    SELECT message
    FROM {keys.DISCORD_LOGS_TABLE_NAME}
    WHERE servername='{servername}'
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    data = [row[0] for row in rows]

    cursor.close()
    cnxn.close()

    # Convert the data to a DataFrame and return
    return pd.DataFrame(data, columns=['message'])


# Run the asynchronous function
loop = asyncio.get_event_loop()
loop.run_until_complete(create_word_cloud("TestServer"))
