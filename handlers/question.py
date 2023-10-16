import asyncio
import openai
from utilities import keys


async def send_message_in_chunks(target, message_content):
    max_chunk_size = 1999
    for i in range(0, len(message_content), max_chunk_size):
        chunk = message_content[i:i + max_chunk_size]
        await target.send(chunk)


async def handle_question(question_message, target):
    max_retries = 5
    retry_count = 0

    await target.send("Working on your question...⏳")

    try:
        response = openai.ChatCompletion.create(
            model=keys.MODEL_ENGINE,
            messages=[
                {"role": "system", "content": "You are an expert assistant knowledgeable in a wide range of subjects."},
                {"role": "user", "content": question_message.content},
            ]
        )

        # Check if there are choices in the response
        if 'choices' in response and response['choices']:
            # Get the response content
            response_content = response['choices'][0]['message']['content']

            # Send the response in chunks of 1999 characters to resolve Discord's message length limit
            await send_message_in_chunks(target, response_content)
        else:
            await target.send("Sorry, I couldn't generate a response at the moment.")

    except openai.error.RateLimitError:
        while retry_count < max_retries:
            wait_time = (2 ** retry_count) + 1
            await asyncio.sleep(wait_time)
            retry_count += 1

        await target.send("Sorry, I was unable to process your request due to rate limits.")
    except openai.error.OpenAIError as e:
        error_message = f"Encountered an error while processing your request: {e}"
        await target.send(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        await target.send(error_message)
