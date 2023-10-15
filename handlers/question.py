import openai
import time
from utilities import keys


async def handle_question(question_message, target):
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=keys.MODEL_ENGINE,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": (question_message.content + "(It is crucial you keep your response "
                                                                            "under 1999 characters.")},
                ]
            )
            await target.send(response['choices'][0]['message']['content'])
            break
        except openai.error.RateLimitError:
            wait_time = (2 ** retry_count) + 1
            time.sleep(wait_time)
            retry_count += 1
        except openai.error.OpenAIError as e:
            error_message = f"Encountered an error while processing your request: {e}"
            await target.send(error_message)
            break
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            await target.send(error_message)
            break
