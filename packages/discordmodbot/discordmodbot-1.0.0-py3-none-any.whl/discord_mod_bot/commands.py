import discord
from discord.ext import commands
from typing import Optional, List
from .utils import parse_duration, format_duration, create_embed, has_permissions, get_user_from_mention
from .database import DatabaseManager

class ModerationCommands(commands.Cog):
    def __init__(self, bot, config, db: DatabaseManager):
        self.bot = bot
        self.config = config
        self.db = db

    async def cog_check(self, ctx):
        """Check if command is enabled"""
        command_name = ctx.command.name if ctx.command else "unknown"
        return self.config.is_command_enabled(command_name)

    async def log_action(self, ctx, action: str, target: discord.User, reason: str, duration: str = None):
        """Log moderation action"""
        case_id = self.db.add_case(target.id, ctx.author.id, action, reason, duration)

        if self.config.log_channel_id:
            log_channel = self.bot.get_channel(self.config.log_channel_id)
            if log_channel:
                embed = create_embed(
                    f"Case #{case_id} | {action.title()}",
                    f"**User:** {target} ({target.id})\n**Moderator:** {ctx.author}\n**Reason:** {reason}"
                )
                if duration:
                    embed.add_field(name="Duration", value=duration, inline=True)
                await log_channel.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, user: str, *, reason: str = "No reason provided"):
        """Ban a user"""
        target = await get_user_from_mention(ctx, user)
        if not target:
            return await ctx.send(self.config.get_message("user_not_found"))

        try:
            await ctx.guild.ban(target, reason=reason)
            await self.log_action(ctx, "ban", target, reason)
            await ctx.send(self.config.get_message("ban_success").format(user=target, reason=reason))
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this user!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, user: str, *, reason: str = "No reason provided"):
        """Kick a user"""
        target = await get_user_from_mention(ctx, user)
        if not target or not isinstance(target, discord.Member):
            return await ctx.send(self.config.get_message("user_not_found"))

        try:
            await target.kick(reason=reason)
            await self.log_action(ctx, "kick", target, reason)
            await ctx.send(self.config.get_message("kick_success").format(user=target, reason=reason))
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this user!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout_user(self, ctx, user: str, duration: str, *, reason: str = "No reason provided"):
        """Timeout a user"""
        target = await get_user_from_mention(ctx, user)
        if not target or not isinstance(target, discord.Member):
            return await ctx.send(self.config.get_message("user_not_found"))

        duration_seconds = parse_duration(duration)
        if not duration_seconds:
            return await ctx.send(self.config.get_message("invalid_duration"))

        try:
            timeout_until = discord.utils.utcnow() + discord.timedelta(seconds=duration_seconds)
            await target.timeout(timeout_until, reason=reason)
            await self.log_action(ctx, "timeout", target, reason, format_duration(duration_seconds))
            await ctx.send(self.config.get_message("timeout_success").format(user=target, duration=format_duration(duration_seconds), reason=reason))
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to timeout this user!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, user: str, *, reason: str = "No reason provided"):
        """Warn a user"""
        target = await get_user_from_mention(ctx, user)
        if not target:
            return await ctx.send(self.config.get_message("user_not_found"))

        warning_id = self.db.add_warning(target.id, ctx.author.id, reason)
        await self.log_action(ctx, "warn", target, reason)
        await ctx.send(self.config.get_message("warn_success").format(user=target, reason=reason))

        # Try to send DM to user
        try:
            await target.send(f"⚠️ You have been warned in {ctx.guild.name}: {reason}")
        except:
            pass  # User has DMs disabled

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_user(self, ctx, user: str, *, reason: str = "No reason provided"):
        """Unban a user"""
        try:
            user_id = int(user.replace('<@', '').replace('>', '').replace('!', ''))
        except ValueError:
            try:
                user_id = int(user)
            except ValueError:
                return await ctx.send(self.config.get_message("user_not_found"))

        try:
            target = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(target, reason=reason)
            await self.log_action(ctx, "unban", target, reason)
            await ctx.send(self.config.get_message("unban_success").format(user=target))
        except discord.NotFound:
            await ctx.send("❌ User is not banned!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="massban")
    @commands.has_permissions(ban_members=True)
    async def mass_ban(self, ctx, users: str, *, reason: str = "No reason provided"):
        """Mass ban multiple users"""
        user_list = users.split()
        banned_count = 0
        failed_count = 0

        for user_str in user_list:
            target = await get_user_from_mention(ctx, user_str)
            if target:
                try:
                    await ctx.guild.ban(target, reason=reason)
                    await self.log_action(ctx, "ban", target, reason)
                    banned_count += 1
                except:
                    failed_count += 1
            else:
                failed_count += 1

        await ctx.send(f"✅ Mass ban completed: {banned_count} users banned, {failed_count} failed.")

    @commands.command(name="cases")
    async def view_cases(self, ctx, user: Optional[str] = None, limit: int = 10):
        """View moderation cases"""
        user_id = None
        if user:
            target = await get_user_from_mention(ctx, user)
            if target:
                user_id = target.id

        cases = self.db.get_cases(user_id, limit)

        if not cases:
            return await ctx.send("No cases found.")

        embed = create_embed("Moderation Cases", "Recent moderation actions")

        for case in cases[:10]:  # Limit to 10 for embed
            target_user = self.bot.get_user(case.user_id)
            moderator = self.bot.get_user(case.moderator_id)

            embed.add_field(
                name=f"Case #{case.case_id} - {case.action.title()}",
                value=f"User: {target_user or 'Unknown'}\nMod: {moderator or 'Unknown'}\nReason: {case.reason}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="unwarn")
    @commands.has_permissions(manage_messages=True)
    async def unwarn_user(self, ctx, warning_id: int):
        """Remove a warning"""
        success = self.db.remove_warning(warning_id)
        if success:
            await ctx.send(f"✅ Warning #{warning_id} has been removed!")
        else:
            await ctx.send("❌ Warning not found or already removed!")

    @commands.command(name="warnings")
    async def view_warnings(self, ctx, user: str):
        """View warnings for a user"""
        target = await get_user_from_mention(ctx, user)
        if not target:
            return await ctx.send(self.config.get_message("user_not_found"))

        warnings = self.db.get_warnings(target.id)

        if not warnings:
            return await ctx.send(f"{target} has no active warnings.")

        embed = create_embed(f"Warnings for {target}", f"Total active warnings: {len(warnings)}")

        for warning in warnings[:10]:  # Limit to 10
            moderator = self.bot.get_user(warning['moderator_id'])
            embed.add_field(
                name=f"Warning #{warning['warning_id']}",
                value=f"Reason: {warning['reason']}\nMod: {moderator or 'Unknown'}\nDate: {warning['timestamp'][:10]}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="userinfo")
    async def user_info(self, ctx, user: str):
        """Get user moderation info"""
        target = await get_user_from_mention(ctx, user)
        if not target:
            return await ctx.send(self.config.get_message("user_not_found"))

        stats = self.db.get_user_stats(target.id)
        warnings = self.db.get_warnings(target.id)

        embed = create_embed(f"User Info: {target}", f"ID: {target.id}")
        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)

        if stats:
            stats_text = "\n".join([f"{action.title()}: {count}" for action, count in stats.items()])
            embed.add_field(name="Moderation History", value=stats_text or "None", inline=True)

        embed.add_field(name="Active Warnings", value=len(warnings), inline=True)

        if isinstance(target, discord.Member):
            embed.add_field(name="Joined Server", value=target.joined_at.strftime("%Y-%m-%d"), inline=True)

        await ctx.send(embed=embed)