import asyncio
import io
import discord
from utilities import keys
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from wordcloud import WordCloud
from configurations.commands import prefixed_commands
from database.db import connect_to_db
from discord.errors import HTTPException

executor = ThreadPoolExecutor()


async def create_word_cloud(servername, channel, is_private):
    # Check if in private message
    if is_private:
        await channel.send("Sorry, you cannot see word clouds in private messages.")
        return

    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(executor, fetch_data, servername)

    # Check if data is retrieved successfully
    if df.empty:
        return await channel.send(f"No messages retrieved for {servername}.")

    text = ' '.join(df['message'])
    try:
        wordcloud = WordCloud(background_color='white').generate(text)
    except ValueError as e:
        return await channel.send(f"There is not enough data to generate a word cloud for {servername}.")

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('images/wordcloud.png')  # Save the plot to an "images" directory

    try:
        await send_word_cloud_image(channel)
    except HTTPException:
        await channel.send("Error sending the word cloud image. The image might be too large.")


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
    with open('images/wordcloud.png', 'rb') as f:
        image_bytes = f.read()

    # Create a bytes-like object and send it as a Discord message with an embed
    image_file = discord.File(io.BytesIO(image_bytes), filename='wordcloud.png')

    # Create an embed message with the image attachment
    embed = discord.Embed()
    embed.set_image(url='attachment://wordcloud.png')  # Set the image URL to the attachment

    # Send the embedded message with the image
    await channel.send(embed=embed, file=image_file)
