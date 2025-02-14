import discord
import random
from discord.ext import commands
from discord import app_commands

# Set up bot with a command prefix
intents = discord.Intents.default()
intents.members = True  # Enable member intents
intents.messages = True  # Enable message intents
bot = commands.Bot(command_prefix="!", intents=intents)

# List of banned words for automod
banned_words = ["fuck", "bitch", "nigger", "idiot"]


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for word in banned_words:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention}, please avoid using inappropriate language!")
            return

    await bot.process_commands(message)


@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@bot.tree.command(name="bully")
async def bully(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.")
        return

    members = [member for member in interaction.guild.members if not member.bot]
    if not members:
        await interaction.response.send_message("No valid members to bully!")
        return

    victim = random.choice(members)
    insults = [
        f"{victim.mention}, even your reflection avoids looking at you!",
        f"{victim.mention}, I've seen rocks with more personality than you!",
        f"{victim.mention}, your WiFi signal is stronger than your comebacks!",
        f"{victim.mention}, you're like a cloud... when you disappear, it's a beautiful day!"
    ]

    await interaction.response.send_message(random.choice(insults))


# Run the bot (replace YOUR_BOT_TOKEN with your actual bot token)
bot.run("Place-Token-Here")
