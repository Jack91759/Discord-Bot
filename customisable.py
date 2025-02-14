import discord
import json
import random
import os
import threading
import time
from discord.ext import commands
from flask import Flask, request, jsonify, render_template_string

# File for storing bot token and commands
CONFIG_FILE = "config.json"

# Load or initialize config
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"token": "", "commands": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()
COMMANDS = config.get("commands", {})

# Discord Bot Setup
intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_ready1():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="custom", description="Execute a stored custom command")
async def custom(interaction: discord.Interaction, cmd_name: str):
    """Execute a stored custom command"""
    if cmd_name in COMMANDS:
        await interaction.response.send_message(COMMANDS[cmd_name])
    else:
        await interaction.response.send_message("❌ Command not found.")

@bot.tree.command(name="restart")
async def restart(ctx):
    """Restart the bot"""
    await ctx.send("🔄 Restarting...")
    os.execv(__file__, ["python"] + os.sys.argv)

@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
async def eightball(interaction: discord.Interaction, question: str):
    """Get answers from the magic 8-ball"""
    responses = ["Yes", "No", "Maybe", "Ask again later."]
    await interaction.response.send_message(f"🎱 **{random.choice(responses)}**")

@bot.tree.command(name="serverinfo", description="Get information about this server")
async def serverinfo(interaction: discord.Interaction):
    """Display server information"""
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Info: {guild.name}", color=discord.Color.blurple())
    embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
    embed.add_field(name="Members", value=guild.member_count, inline=False)
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
        await interaction.response.send_message("⚠️ Invalid equation!")

# Flask Web Interface
app = Flask(__name__)

HTML_PAGE = """  
<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>Discord Bot Manager</title>  
    <style>
        body { font-family: Arial, sans-serif; background: #222; color: #fff; text-align: center; }
        input, button { padding: 10px; margin: 10px; }
        button { background: blue; color: white; border: none; cursor: pointer; }
        ul { list-style-type: none; padding: 0; }
    </style>
</head>  
<body>  
    <h1>Discord Bot Manager</h1>  
    <input type="text" id="token" placeholder="Bot Token" value="{{ token }}">  
    <button onclick="setToken()">Save Token</button>  
    <h2>Add Custom Command</h2>
    <input type="text" id="command" placeholder="Command Name">  
    <input type="text" id="response" placeholder="Response">  
    <button onclick="addCommand()">Add Command</button>  
    <h2>Commands</h2>  
    <ul id="commands"></ul>  
    <button onclick="restartBot()">Restart Bot</button>  

    <script>  
        async function setToken() {
            const token = document.getElementById('token').value;
            const res = await fetch('/set_token', {  
                method: 'POST',  
                headers: { 'Content-Type': 'application/json' },  
                body: JSON.stringify({ token })  
            });  
            alert(await res.json());
        }

        async function addCommand() {  
            const command = document.getElementById('command').value;  
            const response = document.getElementById('response').value;  
            if (!command || !response) return alert("Fill both fields!");  

            const res = await fetch('/add_command', {  
                method: 'POST',  
                headers: { 'Content-Type': 'application/json' },  
                body: JSON.stringify({ command, response })  
            });  
            alert(await res.json());  
            loadCommands();  
        }  

        async function loadCommands() {  
            const res = await fetch('/get_commands');  
            const data = await res.json();  
            document.getElementById('commands').innerHTML = Object.keys(data)
                .map(cmd => `<li><b>${cmd}:</b> ${data[cmd]}</li>`)
                .join("");  
        }  

        async function restartBot() {
            await fetch('/restart');
            alert("Restarting bot...");
        }

        loadCommands();  
    </script>  
</body>  
</html>  
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE, token=config["token"])

@app.route("/set_token", methods=["POST"])
def set_token():
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"error": "Missing token"}), 400

    config["token"] = token
    save_config(config)

    return jsonify({"message": "Token updated!"})

@app.route("/add_command", methods=["POST"])
def add_command():
    data = request.json
    cmd_name = data.get("command")
    response = data.get("response")

    if not cmd_name or not response:
        return jsonify({"error": "Missing command name or response"}), 400

    COMMANDS[cmd_name] = response
    config["commands"] = COMMANDS
    save_config(config)

    return jsonify({"message": f"Command '{cmd_name}' added!"})

@app.route("/get_commands", methods=["GET"])
def get_commands():
    return jsonify(COMMANDS)

@app.route("/restart", methods=["GET"])
def restart():
    os.execv(__file__, ["python"] + os.sys.argv)

# Fix: Keep waiting for a token instead of closing
def run_discord_bot():
    while True:
        config = load_config()
        token = config["token"]
        if token:
            bot.run(token)
        else:
            print("⚠️ Set bot token in the web interface!")
            time.sleep(10)  # Wait before retrying

# Run Flask and Discord bot simultaneously
def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_discord_bot()
