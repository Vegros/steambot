import discord
from discord import app_commands
from discord.ext import commands
from data_handler import Handler
import os
from fetch_from_api import Api
import re
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Enable if your bot needs to read message content
intents.members = True  # Enable if your bot needs to access member information

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print(f'Logged in as {bot.user}')
    try:
        synced = await  bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)


@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}, how are you doing")


@bot.tree.command(name='listfiles')
async def list_files(interaction: discord.Interaction):
    current_directory = os.getcwd()
    json_files = [f for f in os.listdir(current_directory) if f.endswith('.json') and f != 'game_list.json']

    if not json_files:
        await interaction.response.send_message("No JSON files found in the current directory.")
        return

    print("JSON files in the current working directory:")

    # Prepare a formatted string of JSON files
    files = "\n".join(json_files)
    await interaction.response.send_message(f"JSON files:\n{files}")


@bot.tree.command(name='dev')
@app_commands.describe(game_name="type your game_name (type /listfiles for game_name file)")
async def dev(interaction: discord.Interaction, game_name: str):
    handler = Handler(game_name)
    await interaction.response.send_message(f'The developer of this game is: {handler.get_dev()}')


@bot.tree.command(name='price')
@app_commands.describe(game_name="type your game_name (type /listfiles for game_name file)")
async def price(interaction: discord.Interaction, game_name: str):
    handler = Handler(game_name)
    await interaction.response.send_message(f'The price of this game is: {handler.get_price()}')


@bot.tree.command(name='summary')
@app_commands.describe(game_name="type your game_name (type /listfiles for game_name file)")
async def summary(interaction: discord.Interaction, game_name: str):
    handler = Handler(game_name)
    await interaction.response.send_message(f' {handler.get_summary()}')


@bot.tree.command(name='discount')
@app_commands.describe(game_name="type your game_name (type /listfiles for game_name file)")
async def discount(interaction: discord.Interaction, game_name: str):
    handler = Handler(game_name)
    price = handler.get_price()
    await interaction.response.send_message(f'is on discount : {handler.is_on_discount}')


@bot.tree.command(name='add')
@app_commands.describe(game_name="type your game name")
async def add(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer()
    try:
        api = Api(game_name)
        games_list = api.return_games_found()
        if not games_list:
            await interaction.followup.send(f"No games found for '{game_name}'.")
            return

        options = [
            discord.SelectOption(label=game['game_name'], value=str(game['id']))
            for game in games_list
        ]

        select = discord.ui.Select(placeholder="Choose a game...", options=options, min_values=1, max_values=1)

        async def select_callback(select_interaction: discord.Interaction):
            selected_id = int(select_interaction.data['values'][0])
            selected_game = next((game for game in games_list if game['id'] == selected_id), None)

            if selected_game:
                formatted_name = re.sub(r'_+', '_', selected_game['game_name'].replace('-', '_'))
                api.fetch_game_api(selected_game['appid'], formatted_name)

                await select_interaction.response.send_message(f"Game added: {formatted_name}")
            else:
                await select_interaction.response.send_message("Invalid ID. Please try again.")

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        await interaction.followup.send("Games found:", view=view)

    except Exception as e:
        logging.error(f"Error in add command: {e}")
        await interaction.followup.send(f"An error occurred: {str(e)}")

token = os.getenv("token")
bot.run(token)
