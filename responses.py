import random

COMMAND_PREFIX = '!'
global_question = None


def handle_response(message) -> str:
    global global_question
    p_message = message.lower()

    if p_message == f'{COMMAND_PREFIX}hello':
        return 'Hey there!'

    if p_message == f'{COMMAND_PREFIX}roll':
        return str(random.randint(1, 6))

    if p_message == f'{COMMAND_PREFIX}help':
        return """`
COMMANDS:
!hello - greet the bot
!roll - roll a six-sided die
!question - prompt user to ask a question
!help - display this help message

start message with '%' for private response
` """

    if p_message == f'{COMMAND_PREFIX}question':
        global_question = None
        return 'Please enter your question below:'

    if global_question is not None:
        global_question = message.content
        return 'Thanks, your question has been recorded!'
