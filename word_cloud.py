import keys
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from db import connect_to_db


def create_word_cloud(servername):
    cnxn, cursor = connect_to_db()

    # SQL query to fetch data
    query = f"""
    SELECT message
    FROM {keys.DISCORD_LOGS_TABLE_NAME}
    WHERE servername='{servername}'
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    data = [row[0] for row in rows]

    # Convert the data to a DataFrame
    df = pd.DataFrame(data, columns=['message'])

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

    cursor.close()
    cnxn.close()
