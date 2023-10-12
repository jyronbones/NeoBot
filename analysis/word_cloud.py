import asyncio
import io
import discord
from database.word_cloud_data_fetch import fetch_data
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from wordcloud import WordCloud
from discord.errors import HTTPException
from database.message_extractors import extract_mentions, extract_links

executor = ThreadPoolExecutor()


def clean_message(message):
    """Clean message by removing mentions and links"""
    for mention in extract_mentions(message):
        message = message.replace(mention, '')
    for link in extract_links(message):
        message = message.replace(link, '')
    return message


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

    # Clean messages
    df['message'] = df['message'].apply(clean_message)

    text = ' '.join(df['message'])
    try:
        wordcloud = WordCloud(background_color='white').generate(text)
    except ValueError:
        return await channel.send(f"There is not enough data to generate a word cloud for {servername}.")

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('images/wordcloud.png')  # Save the plot to an "images" directory

    try:
        await send_word_cloud_image(channel)
    except HTTPException:
        await channel.send("Error sending the word cloud image. The image might be too large.")


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
