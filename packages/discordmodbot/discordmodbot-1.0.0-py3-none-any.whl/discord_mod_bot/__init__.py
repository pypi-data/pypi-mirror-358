
"""
Discord Moderation Bot Library
A comprehensive library for creating Discord moderation bots with minimal code.
"""

from .bot import ModerationBot
from .config import BotConfig
from .database import DatabaseManager

__version__ = "1.0.0"
__all__ = ["ModerationBot", "BotConfig", "DatabaseManager"]
"""
Discord Moderation Bot Library

A comprehensive Discord moderation bot library that provides:
- Complete moderation commands (ban, kick, timeout, warn, etc.)
- Mass moderation capabilities
- Case management with SQLite database
- Warning system with unwarn functionality
- Both slash and prefix command support
- Customizable messages and settings
- Easy configuration and setup

Usage:
    from discord_mod_bot import ModerationBot, BotConfig
    
    config = BotConfig(token="YOUR_TOKEN", prefix="!")
    bot = ModerationBot(config)
    bot.run_bot()
"""

from .bot import ModerationBot
from .config import BotConfig
from .database import DatabaseManager, Case
from .utils import parse_duration, format_duration

__version__ = "1.0.0"
__author__ = "Discord Mod Bot Team"
__email__ = "support@discordmodbot.com"

__all__ = [
    "ModerationBot",
    "BotConfig", 
    "DatabaseManager",
    "Case",
    "parse_duration",
    "format_duration"
]
