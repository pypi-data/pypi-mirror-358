
import discord
from discord.ext import commands
from .config import BotConfig
from .database import DatabaseManager
from .commands import ModerationCommands
from .slash_commands import SlashModerationCommands

class ModerationBot(commands.Bot):
    def __init__(self, config: BotConfig):
        self.config = config
        self.db = DatabaseManager(config.database_path)
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        # Initialize bot
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=None
        )
        
        # Store cogs for later addition
        self._cogs_to_add = []
        
        # Prepare cogs based on configuration
        if config.use_prefix_commands:
            self._cogs_to_add.append(ModerationCommands(self, config, self.db))
        
        if config.use_slash_commands:
            self._cogs_to_add.append(SlashModerationCommands(self, config, self.db))
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        # Add cogs during setup
        for cog in self._cogs_to_add:
            await self.add_cog(cog)
        
        # Sync slash commands if enabled
        if self.config.use_slash_commands:
            try:
                synced = await self.tree.sync()
                print(f'Synced {len(synced)} slash commands')
            except Exception as e:
                print(f'Failed to sync slash commands: {e}')
    
    async def on_ready(self):
        print(f'{self.user} has logged in!')
        print(f'Bot is in {len(self.guilds)} guilds')
        print(f'System mode: {self.config.system_mode}')
        print(f'Prefix: {self.config.prefix}' if self.config.use_prefix_commands else 'Prefix commands disabled')
        print(f'Slash commands: {"Enabled" if self.config.use_slash_commands else "Disabled"}')
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(self.config.get_message("no_permission"))
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(self.config.get_message("user_not_found"))
        elif isinstance(error, commands.CommandNotFound):
            pass  # Ignore unknown commands
        else:
            print(f'Error: {error}')
            await ctx.send(f'An error occurred: {error}')
    
    def run_bot(self):
        """Start the bot"""
        try:
            self.run(self.config.token)
        except discord.LoginFailure:
            print("ERROR: Invalid bot token provided!")
        except Exception as e:
            print(f"ERROR: Failed to start bot: {e}")
    
    def set_prefix(self, new_prefix: str):
        """Update bot prefix"""
        self.config.set_prefix(new_prefix)
        self.command_prefix = new_prefix
    
    def set_system(self, mode: str):
        """Update system mode"""
        self.config.set_system(mode)
        print(f"System mode updated to: {mode}")
