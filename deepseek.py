import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime

intents = discord.Intents.default()
intents.members = True  # Enable member intents
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

@bot.tree.command(name="userinfo", description="Get information about a user")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    """Get detailed information about a server member"""
    member = member or interaction.user
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

    embed = discord.Embed(title=f"User Info: {member.display_name}", color=member.color)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=discord.utils.format_dt(member.joined_at, style='R'), inline=False)
    embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, style='R'), inline=False)

    roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
    embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles) if roles else "None", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="serverinfo", description="Get information about this server")
async def serverinfo(interaction: discord.Interaction):
    """Display server information"""
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Info: {guild.name}", color=discord.Color.blurple())

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
    embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, style='R'), inline=False)
    embed.add_field(name="Channels", value=f"{len(guild.text_channels)} Text | {len(guild.voice_channels)} Voice",
                    inline=False)
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="purge", description="Delete multiple messages (requires manage messages)")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    """Delete up to 100 messages"""
    if not 1 <= amount <= 100:
        return await interaction.response.send_message("Please choose a number between 1 and 100.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages!", ephemeral=True)


@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
async def eightball(interaction: discord.Interaction, question: str):
    """Get answers from the magic 8-ball"""
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
        "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.dark_blue())
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=random.choice(responses), inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="poll", description="Create a reaction poll")
async def poll(interaction: discord.Interaction, question: str, options: str):
    """Create a poll with up to 10 comma-separated options"""
    poll_options = [opt.strip() for opt in options.split(",")]

    if len(poll_options) < 2 or len(poll_options) > 10:
        return await interaction.response.send_message("Please provide 2-10 options separated by commas!",
                                                       ephemeral=True)

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    embed = discord.Embed(title=question, color=discord.Color.gold())

    for i, option in enumerate(poll_options):
        embed.add_field(name=f"Option {i + 1}", value=f"{emojis[i]} {option}", inline=False)

    msg = await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()

    for i in range(len(poll_options)):
        await message.add_reaction(emojis[i])


@bot.tree.command(name="avatar", description="Show a user's avatar")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    """Get a user's avatar"""
    user = user or interaction.user
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

    embed = discord.Embed(title=f"{user.display_name}'s Avatar", color=discord.Color.random())
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="flip", description="Flip a coin")
async def flip(interaction: discord.Interaction):
    """Flip a virtual coin"""
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 The coin landed on **{result}**!")


@bot.tree.command(name="math", description="Do a calculation")
async def math(interaction: discord.Interaction, equation: str):
    """Evaluate a mathematical expression"""
    try:
        result = eval(equation)
        await interaction.response.send_message(f"🧮 **{equation}** = `{result}`")
    except:
        await interaction.response.send_message("⚠️ Invalid equation! Please use proper mathematical formatting.",
                                                ephemeral=True)

bot.run("Place-Token-Here")