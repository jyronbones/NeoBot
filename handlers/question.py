import asyncio
import openai
from utilities import keys


async def handle_question(question_message, target):
    max_retries = 5
    retry_count = 0

    working_message = await target.send("Working on your question...⏳")

    try:
        response = openai.ChatCompletion.create(
            model=keys.MODEL_ENGINE,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": (question_message.content + "(It is crucial you keep your response "
                                                                        "under 1999 characters in length.")},
            ]
        )

        # Limit the response to 2000 characters
        response_content = response['choices'][0]['message']['content'][:2000]

        # Send the limited response to the user
        await target.send(response_content)

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
