import random


async def handle_roll(is_private, message):
    random_number = random.randint(1, 6)

    target = message.channel if not is_private else message.author

    await target.send(f"You rolled a {random_number}!")
