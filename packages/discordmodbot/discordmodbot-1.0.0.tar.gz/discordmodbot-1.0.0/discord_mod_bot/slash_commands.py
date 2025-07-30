import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from .utils import parse_duration, format_duration, create_embed, get_user_from_mention
from .database import DatabaseManager

class SlashModerationCommands(commands.Cog):
    def __init__(self, bot, config, db: DatabaseManager):
        self.bot = bot
        self.config = config
        self.db = db

    async def log_action(self, guild, action: str, target: discord.User, moderator: discord.User, reason: str, case_id: int):
        """Log moderation action to log channel"""
        try:
            if self.config.log_channel_id:
                log_channel = guild.get_channel(self.config.log_channel_id)
                if log_channel:
                    embed = create_embed(
                        f"Moderation Action: {action}",
                        f"**User:** {target} ({target.id})\n**Moderator:** {moderator} ({moderator.id})\n**Reason:** {reason}\n**Case ID:** {case_id}"
                    )
                    await log_channel.send(embed=embed)
        except:
            pass  # Fail silently if logging fails

    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(user="The user to ban", reason="Reason for the ban")
    async def ban_slash(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Ban a user"""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You don't have permission to ban members!", ephemeral=True)
            return

        try:
            await user.ban(reason=reason)
            case_id = self.db.add_case(user.id, interaction.user.id, "ban", reason)

            message = self.config.get_message("ban_success").format(user=user.mention, reason=reason)
            await interaction.response.send_message(message)

            await self.log_action(interaction.guild, "Ban", user, interaction.user, reason, case_id)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to ban user: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(user="The user to kick", reason="Reason for the kick")
    async def kick_slash(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a user"""
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ You don't have permission to kick members!", ephemeral=True)
            return

        try:
            await user.kick(reason=reason)
            case_id = self.db.add_case(user.id, interaction.user.id, "kick", reason)

            message = self.config.get_message("kick_success").format(user=user.mention, reason=reason)
            await interaction.response.send_message(message)

            await self.log_action(interaction.guild, "Kick", user, interaction.user, reason, case_id)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to kick user: {e}", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a user")
    @app_commands.describe(user="The user to timeout", duration="Duration (e.g., 1d, 2h, 30m)", reason="Reason for the timeout")
    async def timeout_slash(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        """Timeout a user"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ You don't have permission to timeout members!", ephemeral=True)
            return

        try:
            duration_seconds = parse_duration(duration)
            if duration_seconds is None:
                await interaction.response.send_message("❌ Invalid duration format! Use: 1d, 2h, 30m, 45s", ephemeral=True)
                return

            timeout_until = discord.utils.utcnow() + discord.timedelta(seconds=duration_seconds)
            await user.timeout(timeout_until, reason=reason)

            case_id = self.db.add_case(user.id, interaction.user.id, "timeout", reason, format_duration(duration_seconds))

            message = self.config.get_message("timeout_success").format(user=user.mention, duration=duration, reason=reason)
            await interaction.response.send_message(message)

            await self.log_action(interaction.guild, "Timeout", user, interaction.user, reason, case_id)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to timeout this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to timeout user: {e}", ephemeral=True)

    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(user="The user to warn", reason="Reason for the warning")
    async def warn_slash(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Warn a user"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You don't have permission to warn members!", ephemeral=True)
            return

        try:
            warning_id = self.db.add_warning(user.id, interaction.user.id, reason)
            case_id = self.db.add_case(user.id, interaction.user.id, "warn", reason)

            message = self.config.get_message("warn_success").format(user=user.mention, reason=reason)
            await interaction.response.send_message(message)

            # Send DM to user
            try:
                await user.send(f"⚠️ You have been warned in {interaction.guild.name}: {reason}")
            except:
                pass  # User has DMs disabled

            await self.log_action(interaction.guild, "Warning", user, interaction.user, reason, case_id)

        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to warn user: {e}", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user by ID")
    @app_commands.describe(user_id="The user ID to unban", reason="Reason for the unban")
    async def unban_slash(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Unban a user by ID"""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ You don't have permission to unban members!", ephemeral=True)
            return

        try:
            user_id_int = int(user_id)
            user = await self.bot.fetch_user(user_id_int)
            await interaction.guild.unban(user, reason=reason)

            case_id = self.db.add_case(user_id_int, interaction.user.id, "unban", reason)
            await interaction.response.send_message(f"✅ {user} has been unbanned!")

            await self.log_action(interaction.guild, "Unban", user, interaction.user, reason, case_id)

        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID!", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found or not banned!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unban user: {e}", ephemeral=True)

    @app_commands.command(name="unwarn", description="Remove a warning by ID")
    @app_commands.describe(warning_id="The warning ID to remove")
    async def unwarn_slash(self, interaction: discord.Interaction, warning_id: int):
        """Remove a warning by ID"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You don't have permission to manage warnings!", ephemeral=True)
            return

        try:
            if self.db.remove_warning(warning_id):
                await interaction.response.send_message(f"✅ Warning #{warning_id} has been removed!")
            else:
                await interaction.response.send_message("❌ Warning not found!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to remove warning: {e}", ephemeral=True)

    @app_commands.command(name="cases", description="View moderation cases")
    @app_commands.describe(user="User to view cases for (optional)", limit="Number of cases to show (default: 10)")
    async def cases_slash(self, interaction: discord.Interaction, user: Optional[discord.Member] = None, limit: int = 10):
        """View moderation cases"""
        try:
            cases = self.db.get_cases(user.id if user else None, limit)

            if not cases:
                await interaction.response.send_message("No cases found!", ephemeral=True)
                return

            embed = create_embed("Moderation Cases", "Recent moderation actions")

            for case in cases[:10]:  # Limit to 10 cases
                user_obj = self.bot.get_user(case.user_id)
                user_name = user_obj.name if user_obj else f"ID: {case.user_id}"

                embed.add_field(
                    name=f"Case #{case.case_id} - {case.action.title()}",
                    value=f"User: {user_name}\nReason: {case.reason}\nDate: {case.timestamp}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to retrieve cases: {e}", ephemeral=True)

    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.describe(user="The user to view warnings for")
    async def warnings_slash(self, interaction: discord.Interaction, user: discord.Member):
        """View warnings for a user"""
        try:
            warnings = self.db.get_warnings(user.id)

            if not warnings:
                await interaction.response.send_message(f"{user.mention} has no active warnings!", ephemeral=True)
                return

            embed = create_embed(f"Warnings for {user.name}", f"Total active warnings: {len(warnings)}")

            for warning in warnings:
                embed.add_field(
                    name=f"Warning #{warning['warning_id']}",
                    value=f"Reason: {warning['reason']}\nDate: {warning['timestamp']}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to retrieve warnings: {e}", ephemeral=True)

    @app_commands.command(name="userinfo", description="Get user moderation statistics")
    @app_commands.describe(user="The user to get info for")
    async def userinfo_slash(self, interaction: discord.Interaction, user: discord.Member):
        """Get user moderation statistics"""
        try:
            stats = self.db.get_user_stats(user.id)
            warnings = self.db.get_warnings(user.id)

            embed = create_embed(f"User Info: {user.name}", f"ID: {user.id}")
            embed.set_thumbnail(url=user.display_avatar.url)

            embed.add_field(name="User ID", value=user.id, inline=True)
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)

            if stats:
                stats_text = "\n".join([f"{action.title()}: {count}" for action, count in stats.items()])
                embed.add_field(name="Moderation History", value=stats_text or "None", inline=False)

            embed.add_field(name="Active Warnings", value=len(warnings), inline=True)

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to get user info: {e}", ephemeral=True)