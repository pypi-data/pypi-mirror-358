
from typing import List, Dict, Optional

class BotConfig:
    def __init__(
        self,
        token: str,
        prefix: str = "!",
        system_mode: str = "prefix&slash",
        enabled_commands: Optional[List[str]] = None,
        custom_messages: Optional[Dict[str, str]] = None,
        log_channel_id: Optional[int] = None,
        database_path: str = "moderation.db"
    ):
        # Validate token
        if not token or token.strip() == "":
            raise ValueError("Bot token is required")
        
        self.token = token.strip()
        
        # Validate and set system mode
        valid_modes = ["prefix&slash", "prefixonly", "slashonly"]
        if system_mode not in valid_modes:
            raise ValueError(f"Invalid system mode. Must be one of: {', '.join(valid_modes)}")
        
        self.system_mode = system_mode
        
        # Set command type flags based on system mode
        if system_mode == "slashonly":
            self.use_slash_commands = True
            self.use_prefix_commands = False
            self.prefix = None  # Not needed for slash-only
        elif system_mode == "prefixonly":
            self.use_slash_commands = False
            self.use_prefix_commands = True
            if not prefix or prefix.strip() == "":
                raise ValueError("A prefix is required when using prefix-only or mixed mode")
            self.prefix = prefix.strip()
        else:  # prefix&slash
            self.use_slash_commands = True
            self.use_prefix_commands = True
            if not prefix or prefix.strip() == "":
                raise ValueError("A prefix is required when using prefix-only or mixed mode")
            self.prefix = prefix.strip()
        
        # Default enabled commands
        if enabled_commands is None:
            self.enabled_commands = [
                "ban", "kick", "timeout", "warn", "unban", "unwarn",
                "massban", "masskick", "masstimeout", "cases", "warnings", "userinfo"
            ]
        else:
            self.enabled_commands = enabled_commands
        
        # Default messages
        self.default_messages = {
            "ban_success": "🔨 {user} has been banned! Reason: {reason}",
            "kick_success": "👢 {user} has been kicked! Reason: {reason}",
            "timeout_success": "⏰ {user} has been timed out for {duration}! Reason: {reason}",
            "warn_success": "⚠️ {user} has been warned! Reason: {reason}",
            "unban_success": "✅ {user} has been unbanned! Reason: {reason}",
            "unwarn_success": "✅ Warning removed successfully!",
            "no_permission": "❌ You don't have permission to use this command!",
            "user_not_found": "❌ User not found!",
            "invalid_duration": "❌ Invalid duration format! Use: 1d, 2h, 30m, 45s",
            "bot_no_permission": "❌ I don't have permission to perform this action!",
            "error": "❌ An error occurred: {error}",
            "mass_ban_success": "🔨 Successfully banned {count} users!",
            "mass_kick_success": "👢 Successfully kicked {count} users!",
            "mass_timeout_success": "⏰ Successfully timed out {count} users!"
        }
        
        # Merge custom messages with defaults
        if custom_messages:
            self.custom_messages = {**self.default_messages, **custom_messages}
        else:
            self.custom_messages = self.default_messages.copy()
        
        self.log_channel_id = log_channel_id
        self.database_path = database_path
    
    def get_message(self, key: str) -> str:
        """Get a message template"""
        return self.custom_messages.get(key, self.default_messages.get(key, f"Message '{key}' not found"))
    
    def set_prefix(self, new_prefix: str):
        """Update the bot prefix"""
        if self.use_prefix_commands:
            if not new_prefix or new_prefix.strip() == "":
                raise ValueError("Prefix cannot be empty when prefix commands are enabled")
            self.prefix = new_prefix.strip()
        else:
            raise ValueError("Cannot set prefix when prefix commands are disabled")
    
    def set_system(self, mode: str):
        """Update system mode"""
        valid_modes = ["prefix&slash", "prefixonly", "slashonly"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid system mode. Must be one of: {', '.join(valid_modes)}")
        
        # Validate prefix requirement for modes that need it
        if mode in ["prefixonly", "prefix&slash"]:
            if not hasattr(self, 'prefix') or not self.prefix or self.prefix.strip() == "":
                raise ValueError("A prefix is required for prefix-only or mixed mode")
        
        self.system_mode = mode
        
        # Update command type flags
        if mode == "slashonly":
            self.use_slash_commands = True
            self.use_prefix_commands = False
        elif mode == "prefixonly":
            self.use_slash_commands = False
            self.use_prefix_commands = True
        else:  # prefix&slash
            self.use_slash_commands = True
            self.use_prefix_commands = True
    
    def is_command_enabled(self, command_name: str) -> bool:
        """Check if a command is enabled"""
        return command_name in self.enabled_commands
    
    def enable_command(self, command_name: str):
        """Enable a command"""
        if command_name not in self.enabled_commands:
            self.enabled_commands.append(command_name)
    
    def disable_command(self, command_name: str):
        """Disable a command"""
        if command_name in self.enabled_commands:
            self.enabled_commands.remove(command_name)
