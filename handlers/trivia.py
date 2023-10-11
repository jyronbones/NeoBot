import asyncio
import requests
import random
from configurations import config


async def handle_trivia(client, is_private, message):
    # Fetch the trivia data
    response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
    data = response.json()["results"][0]

    # Send the question to the user
    question = f"**Category:** {data['category']}\n\n{data['question']}\n\n"

    # Add the answer choices
    choices = data['incorrect_answers'] + [data['correct_answer']]
    random.shuffle(choices)
    for i, choice in enumerate(choices):
        question += f"{i + 1}. {choice}\n"

    target = message.channel if not is_private else message.author
    await target.send(question + "\nPlease enter the number of the correct answer.")

    # Wait for the user to respond with an answer
    try:
        answer_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and m.channel == message.channel and m.content.isdigit() and 1 <= int(m.content) <= len(choices)
        )
        user_answer = int(answer_message.content) - 1
        correct_answer = choices.index(data['correct_answer'])
        if user_answer == correct_answer:
            await target.send("Correct! :white_check_mark: \nYou answered correctly.")
        else:
            await target.send(f"Incorrect! :x: \nThe correct answer was **{data['correct_answer']}**.")
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to answer.")
