
async def handle_commands(commands, prefix, message, is_private):
    """Handles the 'commands' command and sends a list of available commands."""

    command_list = _get_command_list(commands, prefix)
    target = message.channel if not is_private else message.author
    await target.send(command_list)


def _get_command_list(commands, prefix):
    """Construct and return a list of available commands."""
    command_list = "Available commands:\n```"
    for cmd, desc in commands.items():
        command_list += f"\n• {prefix}{cmd}: {desc}"
    command_list += "```"
    return command_list
