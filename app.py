import discord
from discord.ext import commands
from discord import app_commands

# Set up bot with a command prefix
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="pinged")
async def pinged(interaction: discord.Interaction):
    await interaction.response.send_message("Ponger!")


# Run the bot (replace YOUR_BOT_TOKEN with your actual bot token)
bot.run("Place-Token-Here")
