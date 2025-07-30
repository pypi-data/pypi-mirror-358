
# Discord Moderation Bot Library

[![PyPI version](https://badge.fury.io/py/discordmodbot.svg)](https://badge.fury.io/py/discordmodbot)
[![Python versions](https://img.shields.io/pypi/pyversions/discordmodbot.svg)](https://pypi.org/project/discordmodbot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, production-ready Python library for creating Discord moderation bots with minimal code. This library handles all the complex moderation functionality, database management, and logging, so you can focus on customizing your bot.

## 🚀 Features

- **Complete Moderation Commands**: Ban, kick, timeout, warn, mass actions, and more
- **Dual Command Support**: Both slash commands and prefix commands with flexible configuration
- **Advanced Case Management**: SQLite database with full case tracking and history
- **Warning System**: Comprehensive warning management with unwarn functionality
- **Mass Moderation**: Mass ban, kick, and timeout capabilities for efficient moderation
- **Customizable Messages**: Easy configuration for all bot responses and messages
- **Permission Handling**: Automatic permission checking and validation
- **Logging System**: Automatic moderation log channel support with detailed embed logs
- **User Statistics**: View user moderation history and comprehensive statistics
- **Production Ready**: Built for scale with proper error handling and database management

## 📦 Installation

```bash
pip install discordmodbot
```

## 🚀 Quick Start (30 seconds to working bot!)

```python
from discord_mod_bot import ModerationBot, BotConfig

# Simple configuration - just add your bot token!
config = BotConfig(
    token="YOUR_BOT_TOKEN_HERE",
    prefix="!",
    system_mode="prefix&slash"  # Enable both slash and prefix commands
)

# Create and run the bot
bot = ModerationBot(config)
bot.run_bot()
```

That's it! Your moderation bot is now running with ALL features enabled.

## 🎮 Available Commands

### Core Moderation Commands
| Command | Slash | Prefix | Description |
|---------|-------|--------|-------------|
| Ban | `/ban` | `!ban` | Ban a user from the server |
| Kick | `/kick` | `!kick` | Kick a user from the server |
| Timeout | `/timeout` | `!timeout` | Timeout a user for specified duration |
| Warn | `/warn` | `!warn` | Issue a warning to a user |
| Unban | `/unban` | `!unban` | Unban a user by ID |
| Unwarn | `/unwarn` | `!unwarn` | Remove a warning by ID |

### Mass Moderation Commands
| Command | Slash | Prefix | Description |
|---------|-------|--------|-------------|
| Mass Ban | `/massban` | `!massban` | Ban multiple users at once |
| Mass Kick | `/masskick` | `!masskick` | Kick multiple users at once |
| Mass Timeout | `/masstimeout` | `!masstimeout` | Timeout multiple users at once |
| Mass Unban | `/massunban` | `!massunban` | Unban multiple users at once |

### Information & Management Commands
| Command | Slash | Prefix | Description |
|---------|-------|--------|-------------|
| Cases | `/cases` | `!cases` | View moderation case history |
| Warnings | `/warnings` | `!warnings` | View user warnings |
| User Info | `/userinfo` | `!userinfo` | Get detailed user moderation statistics |

## ⚙️ System Configuration Options

The library supports three different system modes:

### 1. Mixed Mode (Recommended)
```python
config = BotConfig(
    token="YOUR_TOKEN",
    prefix="!",
    system_mode="prefix&slash"  # Both slash and prefix commands
)
```

### 2. Prefix Only Mode
```python
config = BotConfig(
    token="YOUR_TOKEN", 
    prefix="!",
    system_mode="prefixonly"  # Only prefix commands
)
```

### 3. Slash Only Mode
```python
config = BotConfig(
    token="YOUR_TOKEN",
    system_mode="slashonly"  # Only slash commands
)
```

## 🔧 Advanced Configuration

```python
from discord_mod_bot import ModerationBot, BotConfig

config = BotConfig(
    token="YOUR_BOT_TOKEN_HERE",
    prefix="!",
    system_mode="prefix&slash",
    
    # Enable/disable specific commands
    enabled_commands=[
        "ban", "kick", "timeout", "warn", "unban", "unwarn",
        "massban", "masskick", "masstimeout", "massunban",
        "cases", "warnings", "userinfo"
    ],
    
    # Custom messages with placeholders
    custom_messages={
        "ban_success": "🔨 {user} has been banned! Reason: {reason}",
        "kick_success": "👢 {user} has been kicked! Reason: {reason}",
        "timeout_success": "⏰ {user} timed out for {duration}! Reason: {reason}",
        "warn_success": "⚠️ {user} has been warned! Reason: {reason}",
        "no_permission": "❌ You don't have permission to use this command!",
        "user_not_found": "❌ User not found!",
        "invalid_duration": "❌ Invalid duration format! Use: 1d, 2h, 30m, 45s"
    },
    
    # Moderation log channel (optional)
    log_channel_id=123456789012345678,
    
    # Database location (optional)
    database_path="moderation.db"
)

bot = ModerationBot(config)

# Add your own custom commands
@bot.command(name="ping")
async def ping_command(ctx):
    await ctx.send("Pong! 🏓")

@bot.command(name="serverinfo")
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Server Info", color=0x00ff00)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

# Runtime configuration changes
bot.set_prefix("$")  # Change prefix dynamically
bot.set_system("slashonly")  # Change system mode

bot.run_bot()
```

## 📋 Configuration Reference

### BotConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | str | Required | Your Discord bot token |
| `prefix` | str | "!" | Command prefix (required for prefix modes) |
| `system_mode` | str | "prefix&slash" | System mode: "prefix&slash", "prefixonly", "slashonly" |
| `enabled_commands` | list | All | List of enabled command names |
| `custom_messages` | dict | {} | Custom message templates |
| `log_channel_id` | int | None | Channel ID for moderation logs |
| `database_path` | str | "moderation.db" | SQLite database file path |

### Custom Message Placeholders

Available placeholders for custom messages:

| Placeholder | Description | Available In |
|-------------|-------------|--------------|
| `{user}` | Target user mention | All commands |
| `{reason}` | Provided reason | All commands |
| `{duration}` | Timeout duration | Timeout commands |
| `{moderator}` | Moderator mention | Log messages |
| `{case_id}` | Case ID number | Log messages |

## ⏰ Duration Format

For timeout commands, use these intuitive formats:

| Format | Description | Example |
|--------|-------------|---------|
| `1d` | Days | 1 day |
| `2h` | Hours | 2 hours |
| `30m` | Minutes | 30 minutes |
| `45s` | Seconds | 45 seconds |
| `1d2h30m` | Combined | 1 day, 2 hours, 30 minutes |

**Examples:**
- `!timeout @user 30m Spamming` - 30 minute timeout
- `!timeout @user 1d2h Being disruptive` - 1 day 2 hour timeout
- `/timeout user:@user duration:24h reason:Rule violation` - 24 hour timeout

## 🗄️ Database Structure

The library automatically creates and manages an SQLite database with these tables:

### Cases Table
Stores all moderation actions with complete history:
- `case_id` - Unique case identifier
- `user_id` - Target user ID
- `moderator_id` - Moderator user ID
- `action` - Action type (ban, kick, timeout, warn, etc.)
- `reason` - Reason provided
- `timestamp` - When action occurred
- `duration` - Duration for timeouts

### Warnings Table
Manages user warnings:
- `warning_id` - Unique warning identifier
- `user_id` - User who was warned
- `moderator_id` - Moderator who issued warning
- `reason` - Warning reason
- `timestamp` - When warning was issued
- `active` - Whether warning is still active

### Guild Settings Table
Per-server configuration:
- `guild_id` - Discord guild/server ID
- `prefix` - Custom prefix for the server
- `log_channel_id` - Moderation log channel
- `enabled_commands` - JSON list of enabled commands

## 🔐 Required Permissions

Your bot needs these Discord permissions:

### Essential Permissions
- `Ban Members` - For ban/unban commands
- `Kick Members` - For kick commands
- `Moderate Members` - For timeout commands
- `Manage Messages` - For warning system
- `Send Messages` - Basic functionality
- `Use Slash Commands` - For slash commands
- `Embed Links` - For rich embeds
- `Read Message History` - For context

### Optional Permissions
- `Manage Channels` - For advanced features
- `View Audit Log` - For enhanced logging

## 🔧 Bot Setup Guide

### 1. Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name and create

### 2. Create Bot User
1. Go to "Bot" section
2. Click "Add Bot"
3. Copy the bot token
4. Enable "Message Content Intent" under "Privileged Gateway Intents"

### 3. Invite Bot to Server
1. Go to "OAuth2" > "URL Generator"
2. Select "bot" and "applications.commands" scopes
3. Select required permissions
4. Use generated URL to invite bot

### 4. Implement Bot
```python
from discord_mod_bot import ModerationBot, BotConfig

config = BotConfig(
    token="YOUR_BOT_TOKEN_HERE",  # Paste your token here
    prefix="!",
    system_mode="prefix&slash"
)

bot = ModerationBot(config)
bot.run_bot()
```

## 📚 Usage Examples

### Example 1: Basic Moderation Bot
```python
from discord_mod_bot import ModerationBot, BotConfig

# Minimal setup - perfect for small servers
config = BotConfig(
    token="YOUR_TOKEN",
    prefix="!",
    system_mode="prefix&slash"
)

bot = ModerationBot(config)
bot.run_bot()
```

### Example 2: Custom Messages and Logging
```python
from discord_mod_bot import ModerationBot, BotConfig

config = BotConfig(
    token="YOUR_TOKEN",
    prefix="!",
    system_mode="prefix&slash",
    
    # Custom branding
    custom_messages={
        "ban_success": "🔨 **BANNED** {user} | Reason: {reason}",
        "kick_success": "👢 **KICKED** {user} | Reason: {reason}",
        "timeout_success": "⏰ **TIMEOUT** {user} for {duration} | Reason: {reason}"
    },
    
    # Enable logging
    log_channel_id=123456789012345678
)

bot = ModerationBot(config)
bot.run_bot()
```

### Example 3: Limited Commands for Small Server
```python
from discord_mod_bot import ModerationBot, BotConfig

config = BotConfig(
    token="YOUR_TOKEN",
    prefix="$",
    system_mode="prefixonly",
    
    # Only enable essential commands
    enabled_commands=["warn", "timeout", "kick", "cases", "warnings"]
)

bot = ModerationBot(config)
bot.run_bot()
```

### Example 4: Large Server with All Features
```python
from discord_mod_bot import ModerationBot, BotConfig
import discord

config = BotConfig(
    token="YOUR_TOKEN",
    prefix="!",
    system_mode="prefix&slash",
    
    # All commands enabled
    enabled_commands=[
        "ban", "kick", "timeout", "warn", "unban", "unwarn",
        "massban", "masskick", "masstimeout", "massunban",
        "cases", "warnings", "userinfo"
    ],
    
    # Professional messages
    custom_messages={
        "ban_success": "⚔️ {user} has been permanently banned.\n**Reason:** {reason}\n**Moderator:** {moderator}",
        "kick_success": "👢 {user} has been removed from the server.\n**Reason:** {reason}",
        "timeout_success": "⏰ {user} has been timed out for {duration}.\n**Reason:** {reason}",
        "warn_success": "⚠️ {user} has received a formal warning.\n**Reason:** {reason}",
    },
    
    log_channel_id=987654321098765432,
    database_path="large_server_moderation.db"
)

bot = ModerationBot(config)

# Add custom commands for large server
@bot.command(name="stats")
async def server_stats(ctx):
    total_cases = len(bot.db.get_cases(limit=10000))
    embed = discord.Embed(title="📊 Server Moderation Stats", color=0x3498db)
    embed.add_field(name="Total Cases", value=total_cases, inline=True)
    embed.add_field(name="Active Warnings", value="Coming soon", inline=True)
    await ctx.send(embed=embed)

bot.run_bot()
```

## 🚨 Command Examples

### Basic Commands
```bash
# Prefix commands
!ban @user#1234 Spamming in chat
!kick @user#1234 Breaking rules
!timeout @user#1234 1h Inappropriate behavior
!warn @user#1234 Please follow the rules

# Slash commands
/ban user:@user#1234 reason:Spamming in chat
/kick user:@user#1234 reason:Breaking rules
/timeout user:@user#1234 duration:1h reason:Inappropriate behavior
/warn user:@user#1234 reason:Please follow the rules
```

### Mass Moderation
```bash
# Ban multiple users
!massban @user1 @user2 @user3 Mass spam attack

# Kick multiple users
!masskick @user1 @user2 Coordinated trolling

# Timeout multiple users
!masstimeout @user1 @user2 30m Disrupting event
```

### Information Commands
```bash
# View recent cases
!cases
!cases @user#1234

# View user warnings
!warnings @user#1234

# User moderation info
!userinfo @user#1234
```

## 🛠️ Troubleshooting

### Common Issues

#### "Missing Access" Error
- **Solution:** Ensure bot has required permissions in server settings

#### "Hierarchy Error" 
- **Solution:** Move bot role above target user roles in server settings

#### "Token Invalid" Error
- **Solution:** Regenerate bot token in Discord Developer Portal

#### Commands Not Working
- **Solution:** Check if Message Content Intent is enabled for prefix commands

#### Slash Commands Not Appearing
- **Solution:** Wait up to 1 hour for Discord to sync, or restart Discord client

### Debug Mode
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

config = BotConfig(token="YOUR_TOKEN", prefix="!")
bot = ModerationBot(config)
bot.run_bot()
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/discordmodbot/discordmodbot/issues)
- **Documentation**: [Read the full docs](https://github.com/discordmodbot/discordmodbot/wiki)
- **Discord Server**: [Join our support community](https://discord.gg/pqWMR5gS)

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the Discord moderation community
- Thanks to all contributors and users

---

**Made with ❤️ for the Discord community**
