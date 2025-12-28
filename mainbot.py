import discord
from discord import app_commands
import subprocess
import os

# Railway — read bot token from env var
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = 999664473101058168  # Replace with your Discord ID


class RunModal(discord.ui.Modal, title="Run Auto-Sender"):
    token_input = discord.ui.TextInput(label="Bot Token", placeholder="Enter bot token", required=True)
    channel_id_input = discord.ui.TextInput(label="Channel ID", placeholder="1234567890", required=True)
    interval_input = discord.ui.TextInput(label="Interval (seconds)", placeholder="60", required=True)
    message_input = discord.ui.TextInput(
        label="Message Text",
        placeholder="Message to send",
        style=discord.TextStyle.paragraph,
        required=True
    )
    auto_response_input = discord.ui.TextInput(
        label="Auto-response Text",
        placeholder="DM reply message",
        required=False,
        default="This is an automated reply."
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id_input.value)
            interval = int(self.interval_input.value)

            if interval < 1:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid Channel ID or interval. Try again.",
                ephemeral=True
            )
            return

        try:
            env = os.environ.copy()
            env.update({
                "BOT_TOKEN": self.token_input.value,
                "CHANNEL_ID": str(channel_id),
                "INTERVAL_SECONDS": str(interval),
                "MESSAGE_TEXT": self.message_input.value,
                "AUTO_RESPONSE_TEXT": self.auto_response_input.value
            })

            # Launch automation script
            subprocess.Popen(
                ["python", "selfbot.py"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )

            await interaction.response.send_message(
                "🚀 Auto-Sender started successfully. It is now running in background!",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"⚠ Error launching automation: {str(e)}",
                ephemeral=True
            )


class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = MyBot()


@bot.tree.command(name="run", description="Start auto sending messages")
async def run_cmd(interaction: discord.Interaction):
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ Not authorized.", ephemeral=True)
        return

    await interaction.response.send_modal(RunModal())


@bot.event
async def on_ready():
    print(f"🤖 Bot logged in as {bot.user}")


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Missing BOT_TOKEN in Railway Variables")
    else:
        bot.run(BOT_TOKEN)
