
import re
from typing import Optional

def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse duration string and return seconds
    Supports: 1d, 2h, 30m, 45s, or combinations like 1d2h30m
    """
    if not duration_str:
        return None
    
    # Remove spaces and convert to lowercase
    duration_str = duration_str.replace(" ", "").lower()
    
    # Pattern to match duration components
    pattern = r'(\d+)([dhms])'
    matches = re.findall(pattern, duration_str)
    
    if not matches:
        return None
    
    total_seconds = 0
    time_units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    for value, unit in matches:
        if unit in time_units:
            total_seconds += int(value) * time_units[unit]
        else:
            return None
    
    # Discord timeout limit is 28 days
    max_timeout = 28 * 86400  # 28 days in seconds
    if total_seconds > max_timeout:
        return max_timeout
    
    return total_seconds if total_seconds > 0 else None

def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds:
            return f"{minutes}m{remaining_seconds}s"
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes:
            return f"{hours}h{remaining_minutes}m"
        return f"{hours}h"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours:
            return f"{days}d{remaining_hours}h"
        return f"{days}d"

def validate_user_mention(mention_str: str) -> Optional[int]:
    """
    Extract user ID from mention string
    """
    if not mention_str:
        return None
    
    # Remove <@! or <@ and >
    user_id_str = mention_str.strip('<@!>').strip('<@>')
    
    try:
        return int(user_id_str)
    except ValueError:
        return None

def truncate_string(text: str, max_length: int = 1000) -> str:
    """
    Truncate string to max length with ellipsis
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_case_reason(reason: str) -> str:
    """
    Format and validate case reason
    """
    if not reason or reason.strip() == "":
        return "No reason provided"
    
    # Truncate if too long
    reason = truncate_string(reason.strip(), 500)
    
    return reason

import discord
from discord.ext import commands
from typing import Union

def create_embed(title: str, description: str, color: int = 0x3498db) -> discord.Embed:
    """
    Create a Discord embed with title and description
    """
    embed = discord.Embed(title=title, description=description, color=color)
    embed.timestamp = discord.utils.utcnow()
    return embed

def has_permissions(member: discord.Member, **permissions) -> bool:
    """
    Check if member has specified permissions
    """
    return member.guild_permissions.is_superset(discord.Permissions(**permissions))

async def get_user_from_mention(ctx, user_input: str) -> Union[discord.User, discord.Member, None]:
    """
    Get user from mention string, user ID, or username
    """
    # Try to convert mention to user ID
    user_id = validate_user_mention(user_input)
    
    if user_id:
        try:
            # Try to get member first (if in guild)
            if hasattr(ctx, 'guild') and ctx.guild:
                member = ctx.guild.get_member(user_id)
                if member:
                    return member
            
            # Fallback to fetching user
            user = await ctx.bot.fetch_user(user_id)
            return user
        except:
            pass
    
    # Try parsing as raw user ID
    try:
        user_id = int(user_input)
        if hasattr(ctx, 'guild') and ctx.guild:
            member = ctx.guild.get_member(user_id)
            if member:
                return member
        
        user = await ctx.bot.fetch_user(user_id)
        return user
    except:
        pass
    
    # Try finding by username in guild
    if hasattr(ctx, 'guild') and ctx.guild:
        for member in ctx.guild.members:
            if member.name.lower() == user_input.lower() or member.display_name.lower() == user_input.lower():
                return member
    
    return None
