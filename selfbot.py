import discord
import asyncio
import sys
import os

# Get inputs from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
MESSAGE_TEXT = os.getenv('MESSAGE_TEXT', 'Default message')
INTERVAL_SECONDS = int(os.getenv('INTERVAL_SECONDS', 60))
AUTO_RESPONSE_TEXT = os.getenv('AUTO_RESPONSE_TEXT', 'Auto-response')

print(f"Self-bot starting with TOKEN: {TOKEN[:10]}..., CHANNEL_ID: {CHANNEL_ID}, MESSAGE: {MESSAGE_TEXT}, INTERVAL: {INTERVAL_SECONDS}")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Self-bot logged in as {client.user}')
    while True:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            try:
                await channel.send(MESSAGE_TEXT)
                print(f"Message sent to channel {CHANNEL_ID}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print(f"Channel {CHANNEL_ID} not found")
        await asyncio.sleep(INTERVAL_SECONDS)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        try:
            await message.channel.send(AUTO_RESPONSE_TEXT)
            print("Auto-response sent to DM")
        except Exception as e:
            print(f"Error sending DM response: {e}")

client.run(TOKEN)
