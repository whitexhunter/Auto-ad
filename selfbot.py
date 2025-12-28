import discord
import asyncio
import sys
import os

# Get inputs from environment variables (set by main bot)
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
MESSAGE_TEXT = os.getenv('MESSAGE_TEXT', 'Default message')
INTERVAL_SECONDS = int(os.getenv('INTERVAL_SECONDS', 60))
AUTO_RESPONSE_TEXT = os.getenv('AUTO_RESPONSE_TEXT', 'Auto-response')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Self-bot logged in as {client.user}')
    while True:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(MESSAGE_TEXT)
        await asyncio.sleep(INTERVAL_SECONDS)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        await message.channel.send(AUTO_RESPONSE_TEXT)

client.run(DISCORD_TOKEN)
