import discord
from discord.ext import commands, tasks
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load Google Sheets service account data from .env
google_service_account_data = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_DATA'))

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/spreadsheets", 
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account_data, scope)
client = gspread.authorize(creds)

# Define roles and channels to log
ROLES_TO_PAUSE = [123456789012345678]  # Replace with your role IDs for pausing
LOGGING_CHANNEL_ID = 123456789012345678  # Replace with your logging channel ID

# Emojis for reactions
GREEN_TICK = '✅'
RED_CROSS = '❌'

# Tracking user status updates
user_status_updates = {}
PAUSE_BOT = False

@bot.event
async def on_ready():
    logging_channel = bot.get_channel(LOGGING_CHANNEL_ID)
    if logging_channel:
        await logging_channel.send(f'Bot connected as {bot.user}')
    print('Bot connected')

@bot.event
async def on_message(message):
    global user_status_updates, PAUSE_BOT

    if message.author.bot:
        return
    
    # Check if the bot is paused for the user
    if PAUSE_BOT and any(role.id in ROLES_TO_PAUSE for role in message.author.roles):
        return  # Ignore messages from users with paused roles

    username = str(message.author.nick or message.author.name)
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    content = message.content

    # Initialize user data if not present
    if username not in user_status_updates:
        user_status_updates[username] = {'updates': 0, 'warnings': 0, 'sheet': None}
    
    # If the user's sheet does not exist, create one
    if user_status_updates[username]['sheet'] is None:
        try:
            user_status_updates[username]['sheet'] = client.create(f"{username}_status_updates").sheet1
            user_status_updates[username]['sheet'].append_row(["Timestamp", "Status Update"])
        except Exception as e:
            print(f"Failed to create sheet for {username}: {e}")
            return

    # Append data to user's Google Sheet
    try:
        user_status_updates[username]['sheet'].append_row([timestamp, content])
        
        # Update user's status updates count
        user_status_updates[username]['updates'] += 1
        
        # Send a log message to the logging channel
        log_channel = bot.get_channel(LOGGING_CHANNEL_ID)
        if log_channel:
            log_message = f"Logged message from {username} at {timestamp}: {content}"
            await log_channel.send(log_message)
        
        # Add a green tick reaction to indicate successful saving
        await message.add_reaction(GREEN_TICK)

    except Exception as e:
        # Send a log message to the logging channel if saving failed
        if log_channel:
            await log_channel.send(f"Failed to log message from {username}: {e}")
        # Add a red cross reaction to indicate failed saving
        await message.add_reaction(RED_CROSS)

    # Check for warnings if the user does not meet the status update requirement
    if user_status_updates[username]['updates'] >= 3:  # Requirement: at least 3 updates
        user_status_updates[username]['updates'] = 0  # Reset for the next week
    else:
        user_status_updates[username]['warnings'] += 1
        if user_status_updates[username]['warnings'] == 2:
            # Notify mentors about the user's warnings
            mentors = [member for member in message.guild.members if any(role.name == "Mentor" for role in member.roles)]
            for mentor in mentors:
                await mentor.send(f"{username} has received 2 warnings for insufficient status updates.")
        elif user_status_updates[username]['warnings'] >= 3:
            # Kick the user from the club after 3 warnings
            await message.author.kick(reason="Too many warnings for insufficient status updates.")
            user_status_updates.pop(username)  # Remove user data after kick

@bot.command()
async def pause(ctx):
    global PAUSE_BOT
    PAUSE_BOT = not PAUSE_BOT  # Toggle pause status
    status = "paused" if PAUSE_BOT else "resumed"
    await ctx.send(f"The bot has been {status}.")

@tasks.loop(hours=24)
async def daily_reset():
    global user_status_updates
    for username in user_status_updates.keys():
        user_status_updates[username]['updates'] = 0  # Reset updates daily

daily_reset.start()

# Run the bot
discord_token = os.getenv('DISCORD_TOKEN')
bot.run(discord_token)
