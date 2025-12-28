import discord
from discord import app_commands
import subprocess
import os

# Replace with your bot token
BOT_TOKEN = 'BOT_TOKEN'

# Replace with your Discord user ID to restrict the command
ALLOWED_USER_ID = 999664473101058168

class RunModal(discord.ui.Modal, title="Run Self-Bot"):
    token_input = discord.ui.TextInput(label="Discord Token", placeholder="Enter your user token", required=True)
    channel_id_input = discord.ui.TextInput(label="Channel ID", placeholder="Enter channel ID", required=True)
    interval_input = discord.ui.TextInput(label="Interval (seconds)", placeholder="e.g., 60", required=True)
    message_input = discord.ui.TextInput(label="Message Text", placeholder="Your message", required=True, style=discord.TextStyle.paragraph)
    auto_response_input = discord.ui.TextInput(label="Auto-Response Text", placeholder="DM response", required=False, default="This is an auto-response.")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id_input.value)
            interval = int(self.interval_input.value)
            if interval < 1:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("Invalid channel ID or interval. Please try again.", ephemeral=True)
            return

        try:
            env = os.environ.copy()
            env.update({
                'DISCORD_TOKEN': self.token_input.value,
                'CHANNEL_ID': str(channel_id),
                'MESSAGE_TEXT': self.message_input.value,
                'INTERVAL_SECONDS': str(interval),
                'AUTO_RESPONSE_TEXT': self.auto_response_input.value
            })
            subprocess.Popen(['python', 'selfbot.py'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await interaction.response.send_message("Self-bot launched successfully! It will run in the background.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error launching self-bot: {str(e)}", ephemeral=True)

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="run", description="Launch the self-bot with custom settings")
async def run_command(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return
    modal = RunModal()
    await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')

bot.run(BOT_TOKEN)
