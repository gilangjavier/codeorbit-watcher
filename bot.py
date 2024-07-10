import discord
import time
from discord.ext import tasks
from discord import app_commands
import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('TOKEN')
TIMEOUT = int(os.getenv('TIMEOUT', 60))
NOTIFICATION_INTERVAL = int(os.getenv('NOTIFICATION_INTERVAL', 1))

# Load services from YAML file
with open('services.yaml', 'r') as file:
    services = yaml.safe_load(file)['services']

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

down_services = {}

def format_status(name, status, response_time=None):
    if response_time is not None:
        description = f"**Status:** {status}\n**Response Time:** {response_time:.2f}s\n**Description:** {'Service Running' if status == 200 else 'Service Down, harap segera cek server dan Cloudflare'}"
    else:
        description = f"**Status:** {status}\n**Response Time:** N/A\n**Description:** {'Service Running' if status == 200 else 'Service Down, harap segera cek server dan Cloudflare'}"
    
    message = f"Service {name} normal" if status == 200 else f"Service {name} down, harap segera cek Cloudflare apakah ada serangan"
    return description, message, status

@tree.command(name="check_status", description="Check the status of all services")
async def check_status(interaction: discord.Interaction):
    await interaction.response.defer()
    fields = []

    async with aiohttp.ClientSession() as session:
        for name, url in services.items():
            start_time = time.monotonic()
            try:
                async with session.get(url, timeout=TIMEOUT) as response:
                    end_time = time.monotonic()
                    response_time = end_time - start_time
                    description, message, status = format_status(name, response.status, response_time)
            except aiohttp.ClientConnectorError:
                description, message, status = format_status(name, "No response", None)
            except asyncio.TimeoutError:
                description, message, status = format_status(name, "No response", None)
            except Exception as e:
                description = f"**Status:** Error\n**Response Time:** N/A\n**Description:** {str(e)}"
                message = f"Service {name} encountered an error: {str(e)}"
                status = "Error"

            fields.append((name, description, status))

    all_up = all(status == 200 for _, _, status in fields)
    
    # Set the embed color based on the overall status
    embed_color = discord.Color.green() if all_up else discord.Color.red()
    embed = discord.Embed(title="🛠️ **Service Status**", color=embed_color)
    
    for name, description, status in fields:
        status_emoji = "✅" if status == 200 else "❌"
        embed.add_field(name=f"{status_emoji} {name}", value=description, inline=False)

    # Send a single message with the embed only
    await interaction.followup.send(embed=embed)

@tree.command(name="notification", description="Manage service status notifications")
async def notification(interaction: discord.Interaction, action: str):
    channel_id = interaction.channel_id
    if action == "active":
        check_services.start(channel_id)
        await interaction.response.send_message("Notifications activated.")
    elif action == "disable":
        check_services.stop()
        await interaction.response.send_message("Notifications deactivated.")
    else:
        await interaction.response.send_message("Invalid action. Use 'active' or 'disable'.")

@tasks.loop(minutes=NOTIFICATION_INTERVAL)
async def check_services(channel_id):
    channel = client.get_channel(channel_id)  # Get the channel where the command was run
    fields = []
    async with aiohttp.ClientSession() as session:
        for name, url in services.items():
            start_time = time.monotonic()
            try:
                async with session.get(url, timeout=TIMEOUT) as response:
                    end_time = time.monotonic()
                    response_time = end_time - start_time
                    if response.status != 200:
                        description, message, status = format_status(name, response.status, response_time)
                        fields.append((name, description, status))
                        if name not in down_services:
                            down_services[name] = datetime.now()
                    else:
                        if name in down_services:
                            down_time = down_services.pop(name)
                            recovery_time = datetime.now() - down_time
                            recovery_seconds = recovery_time.total_seconds()
                            recovery_minutes, recovery_seconds = divmod(recovery_seconds, 60)
                            embed = discord.Embed(title="✅ **Service Recovery Alert**", color=discord.Color.green())
                            embed.add_field(name=f"✅ {name}", value=f"**Status:** {response.status}\n**Response Time:** {response_time:.2f}s\n**Recovery Duration:** {int(recovery_minutes)} minutes {int(recovery_seconds)} seconds\n**Description:** Service Running", inline=False)
                            await channel.send(embed=embed)
            except asyncio.TimeoutError:
                description, message, status = format_status(name, "No response", None)
                fields.append((name, description, status))
                if name not in down_services:
                    down_services[name] = datetime.now()
            except aiohttp.ClientConnectorError:
                description, message, status = format_status(name, "No response", None)
                fields.append((name, description, status))
                if name not in down_services:
                    down_services[name] = datetime.now()
            except Exception as e:
                description = f"**Status:** Error\n**Response Time:** N/A\n**Description:** {str(e)}"
                message = f"Service {name} encountered an error: {str(e)}"
                status = "Error"
                fields.append((name, description, status))
                if name not in down_services:
                    down_services[name] = datetime.now()

    if fields:
        embed_color = discord.Color.red()
        embed = discord.Embed(title="🚨 **Service Down Alert**", color=embed_color)
        for name, description, status in fields:
            status_emoji = "❌"
            embed.add_field(name=f"{status_emoji} {name}", value=description, inline=False)
        await channel.send(embed=embed)

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user} and synced commands.')

client.run(TOKEN)
