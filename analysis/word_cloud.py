import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
import keys
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from commands import prefixed_commands
from database.db import connect_to_db

# Import discord module
import discord

executor = ThreadPoolExecutor()


async def create_word_cloud(servername, channel):
    loop = asyncio.get_event_loop()

    # Run the database operations in a separate thread
    df = await loop.run_in_executor(executor, fetch_data, servername)

    # Check if data is retrieved successfully
    if df.empty:
        print("No messages retrieved for the specified servername.")
        return

    # Generate and save the word cloud plot to a file
    text = ' '.join(df['message'])
    wordcloud = WordCloud(background_color='white').generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('wordcloud.png')  # Save the plot to a file

    # Send the word cloud plot as a Discord message
    await send_word_cloud_image(channel)


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

    # Convert the data to a DataFrame
    df = pd.DataFrame(data, columns=['message'])

    # Filter out messages that match commands
    df = df[~df['message'].isin(prefixed_commands)]

    return df


async def send_word_cloud_image(channel):
    # Read the image file as bytes
    with open('wordcloud.png', 'rb') as f:
        image_bytes = f.read()

    # Create a bytes-like object and send it as a Discord message with an embed
    image_file = discord.File(io.BytesIO(image_bytes), filename='wordcloud.png')

    # Create an embed message with the image attachment
    embed = discord.Embed()
    embed.set_image(url='attachment://wordcloud.png')  # Set the image URL to the attachment

    # Send the embedded message with the image
    await channel.send(embed=embed, file=image_file)
