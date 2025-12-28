import discord
from discord import app_commands
import subprocess
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", 0))

class RunModal(discord.ui.Modal, title="Run Self-Bot"):
    token_input = discord.ui.TextInput(label="Discord Token", placeholder="Enter your Discord USER token", required=True)
    channel_id_input = discord.ui.TextInput(label="Channel ID", placeholder="Enter channel ID", required=True)
    interval_input = discord.ui.TextInput(label="Interval (seconds)", placeholder="e.g., 60", required=True)
    message_input = discord.ui.TextInput(label="Message Text", placeholder="Message to auto-send", style=discord.TextStyle.paragraph, required=True)
    auto_response_input = discord.ui.TextInput(label="Auto-Response Text", placeholder="DM reply text", required=False, default="This is an auto-response.")

    async def on_submit(self, interaction: discord.Interaction):
        # Debug: Print raw inputs to check for hidden characters
        print(f"Raw channel_id: '{self.channel_id_input.value}'")
        print(f"Raw interval: '{self.interval_input.value}'")

        try:
            channel_id = int(self.channel_id_input.value)
            interval = int(self.interval_input.value)
            if interval < 1:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("Invalid channel ID or interval.", ephemeral=True)
            return

        try:
            env = os.environ.copy()
            env.update({
                "DISCORD_TOKEN": self.token_input.value,
                "CHANNEL_ID": str(channel_id),
                "MESSAGE_TEXT": self.message_input.value,
                "INTERVAL_SECONDS": str(interval),
                "AUTO_RESPONSE_TEXT": self.auto_response_input.value
            })

            # Launch subprocess without waiting (detached)
            subprocess.Popen(["python3", "selfbot.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Self-bot subprocess launched successfully")

            await interaction.response.send_message("Self-bot started successfully and is now running in background!", ephemeral=True)
        except Exception as e:
            print(f"Error launching self-bot: {e}")
            await interaction.response.send_message(f"Error launching self-bot: {e}", ephemeral=True)

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="run", description="Launch the auto self-bot system")
async def run_cmd(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ You are not authorized.", ephemeral=True)
        return
    modal = RunModal()
    await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f"Bot running as {bot.user}")

bot.run(BOT_TOKEN)
