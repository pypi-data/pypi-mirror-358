import os
import disnake
from disnake.ext import commands

class CoolBot(commands.Bot):
    """
    A custom Bot class that extends disnake's Bot.
    It automatically loads cogs from the './cogs' directory.
    """
    def __init__(self, *args, **kwargs):
        # We pass all arguments to the original disnake.ext.commands.Bot
        super().__init__(*args, **kwargs)
        print("CoolBot is firing up...")

    async def setup_hook(self):
        """This is called once before the bot connects."""
        print("Running setup hook...")
        await self.load_all_cogs()
        print("-" * 20)

    async def on_ready(self):
        """Called when the bot is fully connected and ready."""
        print("-" * 20)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print("CoolBot is ready and listening for commands!")
        print("-" * 20)

    async def load_all_cogs(self, cogs_dir: str = "./cogs"):
        """Finds and loads all command files (cogs) from a directory."""
        print(f"Searching for cogs in '{os.path.abspath(cogs_dir)}'...")
        
        if not os.path.isdir(cogs_dir):
            print(f"Warning: Cogs directory '{cogs_dir}' not found. No cogs will be loaded.")
            return

        for filename in os.listdir(cogs_dir):
            # Cogs are Python files, but we ignore special files like __init__.py
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_path = f"cogs.{filename[:-3]}"  # Format for disnake: 'cogs.general'
                try:
                    self.load_extension(cog_path)
                    print(f"✅ Successfully loaded cog: {cog_path}")
                except Exception as e:
                    print(f"❌ Failed to load cog: {cog_path}")
                    print(f"   Error: {e}")