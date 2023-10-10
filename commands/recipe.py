import asyncio
import requests
from configurations import keys, config


async def handle_recipe(client, is_private, message):
    target = message.channel if not is_private else message.author
    await target.send("What recipe do you want to search for?")

    # Wait for the user to respond with the recipe they want to search for
    try:
        recipe_message = await client.wait_for(
            "message",
            timeout=config.USER_RESPONSE_TIME,
            check=lambda m: m.author == message.author and not m.content.startswith(config.prefix)
        )
    except asyncio.TimeoutError:
        await target.send("Sorry, you took too long to enter a recipe!")
        return

    food = recipe_message.content
    # Search for recipes using the Spoonacular API
    url = f"https://api.spoonacular.com/recipes/complexSearch?query={recipe_message.content}&apiKey={keys.SPOONACULAR_API_KEY}"
    try:
        response = requests.get(url).json()

        if response["results"]:
            recipe = response["results"][0]
            recipe_name = recipe["title"]
            recipe_id = recipe["id"]

            url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={keys.SPOONACULAR_API_KEY}"
            response = requests.get(url).json()

            recipe_instructions = response["instructions"]
            recipe_ingredients = response["extendedIngredients"]

            formatted_ingredients = "\n".join(
                [f"{ingredient['original']} ({ingredient['amount']} {ingredient['unit']})" for ingredient in recipe_ingredients]
            )

            recipe_text = f"**{recipe_name}**\n\nIngredients:\n{formatted_ingredients}\n\nInstructions:\n{recipe_instructions}"
            await target.send(recipe_text[:2000])  # Make sure the message doesn't exceed Discord's 2000-character limit
        else:
            await target.send("No recipes found!")
    except requests.exceptions.HTTPError as e:
        await target.send(str(e))
    except Exception as e:  # catch-all for unexpected errors
        await target.send(f"Sorry, an error occurred: {str(e)}")
