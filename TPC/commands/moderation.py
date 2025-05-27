import disnake
from disnake.ext import commands, tasks
from datetime import timedelta, datetime
from disnake.ui import View, Button
import asyncio
import re
import json
import os

def is_moderator(ctx):
    permissions = ctx.author.guild_permissions
    return permissions.kick_members or permissions.ban_members or permissions.manage_channels or permissions.manage_messages

def is_moderator_check():
    return commands.check(is_moderator)

settings_file = "settings.json"

def load_settings():
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"role_menus": {}}

def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)

settings = load_settings()

class RoleMenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="create_role_menu", description="Creates a customizable role selection menu", default_member_permissions=disnake.Permissions(mute_members=True))
    async def create_role_menu(
        self,
        inter: disnake.ApplicationCommandInteraction,
        title: str = "Role Selection Menu",
        description: str = "Click a button below to add or remove a role.",
        color: str = commands.Param(
            default="green",
            choices=["blue", "purple", "gold", "orange", "red", "yellow", "green", "dark_theme", "fuchsia"]
        ),
        image_url: str = None,
        footer_text: str = None,
        timestamp: bool = False,
    ):
        channel_id = str(inter.channel.id)

        if channel_id in settings["role_menus"]:
            settings["role_menus"][channel_id].update({
                "title": title,
                "description": description,
                "color": color,
                "image_url": image_url,
                "footer_text": footer_text,
                "timestamp": timestamp,
            })
        else:
            settings["role_menus"][channel_id] = {
                "title": title,
                "description": description,
                "color": color,
                "roles": {},
                "image_url": image_url,
                "footer_text": footer_text,
                "timestamp": timestamp,
            }

        save_settings()

        embed_color = getattr(disnake.Color, color, disnake.Color.green)()

        role_menu = settings["role_menus"][channel_id]
        embed = disnake.Embed(
            title=role_menu["title"],
            description=role_menu["description"],
            color=embed_color,
            timestamp=datetime.now() if role_menu["timestamp"] else None,
        )

        if role_menu.get("footer_text"):
            embed.set_footer(text=role_menu["footer_text"])
        if role_menu.get("image_url"):
            embed.set_image(url=role_menu["image_url"])

        components = [
            disnake.ui.Button(
                label=role_name,
                custom_id=f"role_{role_id}",
                style=disnake.ButtonStyle.green
            )
            for role_name, role_id in role_menu["roles"].items()
        ]
        
        rows = [disnake.ui.ActionRow(*components[i:i + 3]) for i in range(0, len(components), 3)]
        await inter.response.send_message(embed=embed, components=rows)

    @commands.slash_command(name="add_role_to_menu", description="Adds a new role to a specific menu", default_member_permissions=disnake.Permissions(mute_members=True))
    async def add_role_to_menu(self, inter: disnake.ApplicationCommandInteraction, role: disnake.Role, name: str):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        channel_id = str(inter.channel.id)

        if channel_id not in settings["role_menus"]:
            await inter.response.send_message("No role menu has been created for this channel.", ephemeral=True)
            return

        role_menu = settings["role_menus"][channel_id]

        if name in role_menu["roles"]:
            await inter.response.send_message(f"A role with the name '{name}' already exists in the menu.", ephemeral=True)
            return

        role_menu["roles"][name] = role.id
        save_settings()

        await inter.response.send_message(f"Role '{name}' has been added to the menu.", ephemeral=True)
        
        
    @commands.slash_command(name="remove_role_from_menu", description="Removes a role from a specific menu", default_member_permissions=disnake.Permissions(mute_members=True))
    async def remove_role_from_menu(self, inter: disnake.ApplicationCommandInteraction, name: str):
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        channel_id = inter.channel.id
        if channel_id not in settings["role_menus"]:
            await inter.response.send_message("No role menu has been created for this channel.", ephemeral=True)
            return

        if name not in settings["role_menus"][channel_id]["roles"]:
            await inter.response.send_message(f"Role {name} is not in the menu.", ephemeral=True)
            return

        del settings["role_menus"][channel_id]["roles"][name]
        save_settings()

        await inter.response.send_message(f"Role {name} has been removed from the role menu.", ephemeral=True)

    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        try:
            custom_id = interaction.data.custom_id
            if custom_id.startswith("role_"):
                role_id = int(custom_id.split("_")[1])
                role = disnake.utils.get(interaction.guild.roles, id=role_id)

                if not role:
                    await interaction.response.send_message("The role could not be found.", ephemeral=True)
                    return

                if role in interaction.author.roles:
                    await interaction.author.remove_roles(role)
                    await interaction.response.send_message(f"The role {role.name} has been removed.", ephemeral=True)
                else:
                    await interaction.author.add_roles(role)
                    await interaction.response.send_message(f"The role {role.name} has been assigned!", ephemeral=True)
        except Exception as e:
            print(f"Error handling button click: {e}")



# vs






@commands.slash_command(description="Mute a user in a voice channel", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def deafen(inter: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str = "No reason provided"):
    if not inter.author.guild_permissions.mute_members:
        embed = disnake.Embed(
            title="❌ Error",
            description="You do not have permission to mute members.",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
        return

    if user.voice and user.voice.channel:
        await user.edit(mute=True)
        embed = disnake.Embed(
            title="🔇 User Muted",
            description=f"**User:** {user.mention}\n**Reason:** {reason}",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed)
    else:
        embed = disnake.Embed(
            title="❌ Error",
            description=f"{user.mention} is not in a voice channel.",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

@commands.slash_command(description="Unmute a user in a voice channel", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def undeafen(inter: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str = "No reason provided"):
    if not inter.author.guild_permissions.mute_members:
        embed = disnake.Embed(
            title="❌ Error",
            description="You do not have permission to unmute members.",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
        return

    if user.voice and user.voice.channel:
        await user.edit(mute=False)
        embed = disnake.Embed(
            title="🔊 User Unmuted",
            description=f"**User:** {user.mention}\n**Reason:** {reason}",
            color=disnake.Color.green()
        )
        await inter.response.send_message(embed=embed)
    else:
        embed = disnake.Embed(
            title="❌ Error",
            description=f"{user.mention} is not in a voice channel.",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
        
@commands.slash_command(description="Move all members from one voice channel to another", default_member_permissions=disnake.Permissions(mute_members=True))
@is_moderator_check()
async def massmove(ctx: disnake.ApplicationCommandInteraction, from_channel: disnake.VoiceChannel, to_channel: disnake.VoiceChannel):
    embed = disnake.Embed(
        title="🔄 Mass Move",
        description=f"Moving all members from {from_channel.mention} to {to_channel.mention}",
        color=disnake.Color.blue()
    )
    for member in from_channel.members:
        await member.move_to(to_channel)
    await ctx.send(embed=embed)
        
########################

@commands.slash_command(
    description="Send a message to a specific channel with optional templates.",
    default_member_permissions=disnake.Permissions(mute_members=True)
)

async def send(
    inter: disnake.ApplicationCommandInteraction,
    channel: disnake.TextChannel,
    title: str,
    message: str,
    template: str = commands.Param(
        default=None,
        choices=[
            "Announcement",
            "Reminder",
            "Event",
            "Warning",
            "Custom",
            "Update",
            "Alert",
            "Info",
            "News",
            "Feedback"
        ]
    ),
    *,
    link: str = None,
    colors: str = commands.Param(
        default='dark_theme',
        choices=['green', 'blue', 'purple', 'magenta', 'gold', 'orange', 'red', 'yellow', 'dark_theme', 'fuchsia', 'teal', 'dark_green', 'dark_gold', 'dark_red', 'dark_teal', 'dark_purple']
    ),
    imageurl: str = None,
    footertext: str = None,
    timenow: bool = False,
    author: bool = False,
    pin: bool = False
):
    # Шаблоны сообщений
    templates = {
        "Announcement": {
            "title": "📢 Announcement",
            "message": "Here's an important announcement! Please pay attention to this important news. More details are coming soon. Stay tuned!",
            "colors": "gold",
            "footertext": "Announcement by the server team"
        },
        "Reminder": {
            "title": "🔔 Reminder",
            "message": "Don't forget about the upcoming event! Mark your calendars now. You wouldn't want to miss it!",
            "colors": "blue",
            "footertext": "Set your reminders!"
        },
        "Event": {
            "title": "🎉 Event Invitation",
            "message": "Join us for an exciting event happening soon! Don't miss out on the fun. We'll have games, prizes, and much more!",
            "colors": "green",
            "footertext": "See you there!"
        },
        "Warning": {
            "title": "⚠️ Warning",
            "message": "Please adhere to the server rules to avoid issues. Repeated offenses may result in penalties. Stay respectful and have fun!",
            "colors": "red",
            "footertext": "Server Moderation Team"
        },
        "Custom": {
            "title": "Custom Message",
            "message": "This is a custom message. Feel free to personalize it as needed.",
            "colors": "dark_theme",
            "footertext": "Custom Footer"
        },
        "Update": {
            "title": "🔄 Update",
            "message": "There has been a recent update. Please check the new changes and features available. Stay informed and keep up with the latest improvements!",
            "colors": "purple",
            "footertext": "Update by the development team"
        },
        "Alert": {
            "title": "🚨 Alert",
            "message": "This is a critical alert! Please take immediate action or be aware of the current situation. Your attention is required!",
            "colors": "red",
            "footertext": "Alert from the server"
        },
        "Info": {
            "title": "ℹ️ Info",
            "message": "Here’s some important information that might interest you. Check it out to stay informed and updated on the latest happenings.",
            "colors": "blue",
            "footertext": "Info provided by the server"
        },
        "News": {
            "title": "📰 News",
            "message": "Catch up on the latest news! This is where we share all the latest updates and news related to the server, community, and events.",
            "colors": "fuchsia",
            "footertext": "News updates"
        },
        "Feedback": {
            "title": "💬 Feedback",
            "message": "We would love to hear your feedback! Share your thoughts, suggestions, or concerns to help us improve the server and community.",
            "colors": "teal",
            "footertext": "Feedback Team"
        }
    }# Если выбран шаблон, использовать предустановленные параметры
    if template and template in templates:
        selected_template = templates[template]
        title = title or selected_template.get("title")
        message = message or selected_template.get("message")
        colors = selected_template.get("colors", colors)
        footertext = footertext or selected_template.get("footertext")

    # Карта цветов
    color_map = {
        'blue': disnake.Color.blue(),
        'purple': disnake.Color.purple(),
        'magenta': disnake.Color.magenta(),
        'gold': disnake.Color.gold(),
        'orange': disnake.Color.orange(),
        'red': disnake.Color.red(),
        'yellow': disnake.Color.yellow(),
        'green': disnake.Color.green(),
        'dark_theme': disnake.Color.dark_theme(),
        'fuchsia': disnake.Color.fuchsia(),
        'teal': disnake.Color.teal(),
        'dark_green': disnake.Color.dark_green(),
        'dark_gold': disnake.Color.dark_gold(),
        'dark_red': disnake.Color.dark_red(),
        'dark_teal': disnake.Color.dark_teal(),
        'dark_purple': disnake.Color.dark_purple(),
    }

    embed_color = color_map.get(colors, disnake.Color.green())
    time = datetime.now() if timenow else None

    embed = disnake.Embed(
        title=title,
        description=message,
        url=link,
        color=embed_color,
        timestamp=time
    )

    if footertext:
        embed.set_footer(text=footertext)

    if imageurl:
        embed.set_image(url=imageurl)

    if author:
        embed.set_author(name=inter.user.name, icon_url=inter.user.avatar.url)

    # Попытки отправки сообщения
    for attempt in range(3):
        try:
            await asyncio.sleep(1)
            message = await channel.send(embed=embed)
            await inter.response.send_message(f"Message sent to channel: {channel.mention}", ephemeral=True)
            
            # Закрепляем сообщение
            if pin:
                await message.pin()
            
            break
        except disnake.HTTPException as e:
            if e.status == 429:  # Лимит запросов
                await inter.response.send_message('Rate limit exceeded. Please try again later.', ephemeral=True)
                return
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
            else:
                await inter.response.send_message('Failed to send the message after multiple attempts. Please try again later.', ephemeral=True)
                
#####################

@commands.slash_command(description="Send message from the bot name", default_member_permissions=disnake.Permissions(mute_members=True))
async def say(ctx, message: str, *, channel: disnake.TextChannel = None):
    if channel:
        await ctx.response.send_message(f'Message sent to channel: {channel.name}', ephemeral=True)
        await channel.send(message)
    else:
        await ctx.response.send_message(f'We send your message', ephemeral=True)
        await ctx.channel.send(message)
        
@commands.slash_command(description="Send a message to a specific person in the server", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def call(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, *, message: str):
    embed_message = disnake.Embed(
        title="📩 Direct Message",
        description=message,
        color=disnake.Color.blue()
    )

    try:
        embed_message.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await member.send(embed=embed_message)
        success_embed = disnake.Embed(
            title="✅ Message Sent",
            description=f"The message has been successfully sent to {member.mention}.",
            color=disnake.Color.green()
        )
        await ctx.send(embed=success_embed)
    except disnake.Forbidden:
        error_embed = disnake.Embed(
            title="❌ Error",
            description="Failed to send the message. Please ensure that I have permission to send messages to this user.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=error_embed)
    except disnake.HTTPException:
        error_embed = disnake.Embed(
            title="❌ Error",
            description="An error occurred while sending the message.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=error_embed)

        
@commands.slash_command(description="Send a message to all members in the server", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def notifyall(ctx: disnake.ApplicationCommandInteraction, message: str):
    guild = ctx.guild
    success_count = 0
    fail_count = 0

    for member in guild.members:
        if member.bot:
            continue
        try:
            await member.send(message)
            success_count += 1
        except disnake.Forbidden:
            fail_count += 1
        except disnake.HTTPException:
            fail_count += 1

    embed = disnake.Embed(
        title="📢 Message Sent",
        description=f"**Messages successfully sent:** {success_count}\n"
                    f"**Failed to send messages:** {fail_count}",
        color=disnake.Color.green()
    )
    await ctx.send(embed=embed)

@notifyall.error
async def dm_error(ctx: disnake.ApplicationCommandInteraction, error: Exception):
    embed = disnake.Embed(
        title="❌ Error",
        description=f"An error occurred: {error}",
        color=disnake.Color.red()
    )
    await ctx.send(embed=embed)
        
        
        
###################       

        
@commands.slash_command(description="Warn member and give a reason", default_member_permissions=disnake.Permissions(mute_members=True))
async def warn(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, *, reason: str = 'Violation of the rules'):
    user_embed = disnake.Embed(
        title="⚠️ Warning",
        description=f"**Reason:** {reason}",
        color=disnake.Color.orange()
    )
    user_embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    user_embed.set_footer(text=f"Warned by {ctx.author.display_name}")

    try:
        await member.send(embed=user_embed)
    except disnake.Forbidden:
        await ctx.send("I can't send a direct message to this user. Please check their DM settings.", ephemeral=True)
        return
    
    channel_embed = disnake.Embed(
        title="⚠️ User Warned",
        description=f"{member.mention} has been warned.\n\n"
                    f"**Reason:** {reason}",
        color=disnake.Color.orange()
    )
    channel_embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    channel_embed.set_footer(text=f"Action taken by {ctx.author.display_name}")
    
    await ctx.send(embed=channel_embed)
        
@commands.slash_command(
    description="Deletes a specific amount of messages, optionally from a specific user.",
    default_member_permissions=disnake.Permissions(moderate_members=True)
)
async def clear(
    inter: disnake.ApplicationCommandInteraction,
    amount: int,
    channel: disnake.TextChannel = None,
    member: disnake.Member = None
):
    if not inter.user.guild_permissions.manage_messages:
        embed = disnake.Embed(
            title="❌ Permission Denied",
            description="You don't have the required permissions to manage messages.",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
        return

    if amount < 1 or amount > 100:
        embed = disnake.Embed(
            title="❌ Invalid Amount",
            description="The amount must be between 1 and 100.",
            color=disnake.Color.red()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
        return

    channel = channel or inter.channel

    try:
        if member:
            def is_member(m):
                return m.author == member

            deleted = await channel.purge(limit=amount, check=is_member)
        else:
            deleted = await channel.purge(limit=amount)

        embed = disnake.Embed(
            title="🗑 Messages Cleared",
            description=(
                f"**Total Messages Deleted:** {len(deleted)}\n"
                f"**Requested by:** {inter.user.mention}\n"
                f"**Channel:** {channel.mention}\n"
                f"**Timestamp:** {disnake.utils.format_dt(inter.created_at, style='F')}"
            ),
            color=disnake.Color.green()
        )

        if member:
            embed.add_field(name="Deleted Messages From", value=member.mention, inline=False)

        embed.set_footer(text="Thank you for keeping the channel clean! ✨")

        await inter.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        error_embed = disnake.Embed(
            title="❌ Error Occurred",
            description=(
                f"An error occurred while trying to delete messages:\n"
                f"```{e}```"
            ),
            color=disnake.Color.red()
        )
        error_embed.set_footer(text="Please try again or contact an administrator.")
        await inter.response.send_message(embed=error_embed, ephemeral=True)
        
@commands.slash_command(description="Kicks the specified user", default_member_permissions=disnake.Permissions(kick_members=True))
@is_moderator_check()
async def kick(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, *, reason=None):
    if ctx.author.top_role <= member.top_role:
        embed = disnake.Embed(
            title="🚫 Kick Failed",
            description="You cannot kick this user because they have a higher or equal role.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)
        return

    try:
        await member.kick(reason=reason)
        
        embed = disnake.Embed(
            title="✅ User Kicked",
            description=f"{member.mention} has been kicked from the server.\n"
                        f"**Reason:** {reason or 'No reason provided.'}",
            color=disnake.Color.red()
        )
        embed.set_footer(text=f"Action taken by {ctx.author.display_name}")
        
        await ctx.send(embed=embed, ephemeral=True)
    except disnake.HTTPException:
        embed = disnake.Embed(
            title="❌ Error",
            description="An error occurred while trying to kick the user. Please try again.",
            color=disnake.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed, ephemeral=True)
         
@commands.slash_command(description="You can report a member", default_member_permissions=disnake.Permissions(mute_members=True))
async def report(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, *, message: str):
    roles = await ctx.guild.fetch_roles()
    await ctx.send("📩 Your report has been sent to moderators and admins.", ephemeral=True)

    for role in roles:
        if role.permissions.kick_members or role.permissions.ban_members:
            for role_member in role.members:
                try:
                    embed = disnake.Embed(
                        title="📝 Member Report",
                        description=f"**Reported by:** {ctx.author.mention}\n"
                                    f"**Member Reported:** {member.mention}\n\n"
                                    f"**Message:** {message}",
                        color=disnake.Color.blue()
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                    await role_member.send(embed=embed)
                except disnake.Forbidden:
                    pass
                 
def parse_time(time_str):
    """
    Разбирает строку времени формата '2h 30m 15s' и возвращает timedelta.
    """
    time_pattern = re.compile(r'(?:(\d+)h)?(?:\s*(\d+)m)?(?:\s*(\d+)s)?')
    match = time_pattern.match(time_str)
    if not match:
        return None
    
    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0
    
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

@commands.slash_command(description="Mutes the specified user for a given duration", default_member_permissions=disnake.Permissions(mute_members=True))
async def mute(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, duration: str, reason: str = "No reason provided"):
    timeout_duration = parse_time(duration)

    if timeout_duration is None or timeout_duration.total_seconds() <= 0:
        embed = disnake.Embed(
            title="❌ Invalid Time Format",
            description=(
                "Please specify a valid duration using one of the following formats:\n"
                "`1h` - 1 hour\n"
                "`30m` - 30 minutes\n"
                "`15s` - 15 seconds\n\n"
                "**Example:** `/mute @user 1h 30m reason`"
            ),
            color=disnake.Color.red()
        )
        embed.set_footer(text="h - hours, m - minutes, s - seconds")
        await ctx.send(embed=embed, ephemeral=True)
        return

    try:
        await member.edit(timeout=disnake.utils.utcnow() + timeout_duration)
        # Сообщение в канал
        embed = disnake.Embed(
            title="🔇 User Muted",
            description=(
                f"{member.mention} has been muted for {duration}.\n"
                f"**Reason:** {reason}\n"
                f"**Muted By:** {ctx.author.mention}"
            ),
            color=disnake.Color.orange()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"Muted on request by {ctx.author.display_name}")
        await ctx.send(embed=embed, ephemeral=True)
        
        # Сообщение в ЛС
        dm_embed = disnake.Embed(
            title="🔇 You have been muted",
            description=(
                f"You have been muted on {ctx.guild.name} for {duration}.\n"
                f"**Reason:** {reason}\n"
                f"**Muted By:** {ctx.author.mention}"
            ),
            color=disnake.Color.orange()
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await member.send(embed=dm_embed)
    except disnake.Forbidden:
        embed = disnake.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to mute this user.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)
    except disnake.HTTPException as e:
        embed = disnake.Embed(
            title="❌ Error",
            description=f"An error occurred: {e}",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)

@commands.slash_command(description="Unmutes the specified user", default_member_permissions=disnake.Permissions(mute_members=True))
async def unmute(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member):
    try:
        await member.edit(timeout=None)
        # Сообщение в канал
        embed = disnake.Embed(
            title="🔊 User Unmuted",
            description=(
                f"{member.mention} has been unmuted.\n"
                f"**Unmuted By:** {ctx.author.mention}"
            ),
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"Unmuted on request by {ctx.author.display_name}")
        await ctx.send(embed=embed, ephemeral=True)
        
        # Сообщение в ЛС
        dm_embed = disnake.Embed(
            title="🔊 You have been unmuted",
            description=(
                f"You have been unmuted on {ctx.guild.name}.\n"
                f"**Unmuted By:** {ctx.author.mention}"
            ),
            color=disnake.Color.green()
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await member.send(embed=dm_embed)
    except disnake.Forbidden:
        embed = disnake.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to unmute this user.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)
    except disnake.HTTPException as e:
        embed = disnake.Embed(
            title="❌ Error",
            description=f"An error occurred: {e}",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)
        
@commands.slash_command(description="Bans the specified user for a given duration", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()  # 
async def ban(ctx: disnake.ApplicationCommandInteraction, action: str, member: disnake.Member, limit: int, *, reason: str = "No reason provided"):
    limit_time = timedelta(days=limit)
    
    try:
        # Ban the user
        await member.ban(reason=reason)
        
        # Create the embed for the channel
        embed = disnake.Embed(
            title="🔨 User Banned",
            description=(
                f"{member.mention} has been banned for {limit} days.\n"
                f"Action: {'Appeal allowed' if action == 'save' else 'Appeal denied'}\n"
                f"Reason: {reason}\n"
                f"Banned By: {ctx.author.mention}"
            ),
            color=disnake.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)
        
        # Notify the banned user in DMs
        dm_embed = disnake.Embed(
            title="🔨 You have been banned",
            description=(
                f"You have been banned from {ctx.guild.name} for {limit} days.\n"
                f"Reason: {reason}\n"
                f"Action: {'You can appeal.' if action == 'save' else 'No appeal allowed.'}"
            ),
            color=disnake.Color.red()
        )
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await member.send(embed=dm_embed)
        
        # Automatically unban after the limit
        await disnake.utils.sleep_until(ctx.message.created_at + limit_time)
        await ctx.guild.unban(member, reason="Automatic unban after the ban duration")
        await ctx.send(f"{member.name} has been automatically unbanned.")
        
    except disnake.Forbidden:
        embed = disnake.Embed(
            title="❌ Permission Denied",
            description="I don't have permission to ban this user.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed)
        
    except disnake.HTTPException as e:
        embed = disnake.Embed(
            title="❌ Error",
            description=f"An error occurred: {e}",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed)


@commands.slash_command(description="Unbans the specified user", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()  # Your custom decorator for moderator check
async def unban(ctx: disnake.ApplicationCommandInteraction, user: disnake.User, *, reason: str = "No reason provided"):
    try:
        # Unban the user
        await ctx.guild.unban(user, reason=reason)

        # Create the embed for the channel
        embed = disnake.Embed(
            title="✅ User Unbanned",
            description=(
                f"{user.mention} has been unbanned.\n"
                f"Reason: {reason}\n"
                f"Unbanned By: {ctx.author.mention}"
            ),
            color=disnake.Color.green()
        )
        await ctx.send(embed=embed)
        
        # Notify the unbanned user in DMs
        dm_embed = disnake.Embed(
            title="✅ You have been unbanned",
            description=(
                f"You have been unbanned from {ctx.guild.name}.\n"
                f"Reason: {reason}\n"
                f"Unbanned By: {ctx.author.mention}"
                f"return: 🔗 [welcome back](https://dsc.gg/storm-warriors)"
            ),
            color=disnake.Color.green()
        )
        await user.send(embed=dm_embed)

    except disnake.NotFound:
        embed = disnake.Embed(
            title="❌ User Not Found",
            description=f"{user.name} is not in the banned users list.",
            color=disnake.Color.red()
        )
        await ctx.send(embed=embed)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
################## ROLES
# Command to add a role to a user
@commands.slash_command(description="Add a role to a user", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def addrank(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, role: disnake.Role):
    if role in member.roles:
        embed = disnake.Embed(
            title="Error",
            description=f"{member.mention} already has the role {role.name}.",
            color=disnake.Color.red()
        )
    else:
        await member.add_roles(role)
        embed = disnake.Embed(
            title="Role Added",
            description=f"Role {role.name} has been added to {member.mention}.",
            color=disnake.Color.green()
        )
    await inter.response.send_message(embed=embed)

# Command to remove a role from a user
@commands.slash_command(description="Remove a role from a user", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def delrank(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, role: disnake.Role):
    if role not in member.roles:
        embed = disnake.Embed(
            title="Error",
            description=f"{member.mention} does not have the role {role.name}.",
            color=disnake.Color.red()
        )
    else:
        await member.remove_roles(role)
        embed = disnake.Embed(
            title="Role Removed",
            description=f"Role {role.name} has been removed from {member.mention}.",
            color=disnake.Color.green()
        )
    await inter.response.send_message(embed=embed)

# Command to get a list of all roles on the server
@commands.slash_command(description="Get a list of all roles on the server", default_member_permissions=disnake.Permissions(mute_members=True))
async def ranks(inter: disnake.ApplicationCommandInteraction):
    roles = inter.guild.roles
    role_list = "\n".join([role.name for role in roles if role != inter.guild.default_role])
    
    embed = disnake.Embed(
        title="List of All Roles",
        description=role_list or "There are no additional roles on this server.",
        color=disnake.Color.blue()
    )
    await inter.response.send_message(embed=embed)

# Command to get information about a role
@commands.slash_command(description="Get information about a role")
async def roleinfo(inter: disnake.ApplicationCommandInteraction, role: disnake.Role):
    embed = disnake.Embed(
        title=f"Role Information: {role.name}",
        color=role.color
    )
    embed.add_field(name="Role ID", value=role.id, inline=True)
    embed.add_field(name="Number of Members with this Role", value=len(role.members), inline=True)
    embed.add_field(name="Color", value=str(role.color), inline=True)
    embed.add_field(name="Mentionable", value=str(role.mentionable), inline=True)
    embed.add_field(name="Created At", value=role.created_at.strftime('%Y-%m-%d'), inline=True)
    
    await inter.response.send_message(embed=embed)
    
@commands.slash_command(description="Give a temporary role to a user", default_member_permissions=disnake.Permissions(ban_members=True))
@is_moderator_check()
async def temprole(ctx: disnake.ApplicationCommandInteraction, member: disnake.Member, role: disnake.Role, duration: str):
    timeout_duration = parse_time(duration)  # Парсинг времени, нужно определить функцию parse_time
    embed = disnake.Embed(
        title="⏳ Temporary Role Assigned",
        description=f"{member.mention} has been given the role {role.mention} for {duration}.",
        color=disnake.Color.orange()
    )
    await member.add_roles(role)
    await ctx.send(embed=embed)

    await disnake.utils.sleep_until(disnake.utils.utcnow() + timeout_duration)
    await member.remove_roles(role)
    await ctx.send(f"{member.mention} has been removed from the role {role.mention} after {duration}.")
    
    
    
# auto 

import asyncio
import disnake
from disnake.ui import View, Button
from disnake.ext import commands, tasks

class AutoSendingView(View):
    def __init__(self, inter, channel, embed, interval):
        super().__init__(timeout=None)
        self.inter = inter
        self.channel = channel
        self.embed = embed
        self.interval = interval
        self.task = None

        self.start_task()

        self.stop_button = Button(label="Stop", style=disnake.ButtonStyle.red)
        self.start_button = Button(label="Start", style=disnake.ButtonStyle.green)
        self.update_button = Button(label="Update Interval", style=disnake.ButtonStyle.blurple)
        self.send_now_button = Button(label="Send Now", style=disnake.ButtonStyle.gray)

        self.add_item(self.stop_button)
        self.add_item(self.start_button)
        self.add_item(self.update_button)
        self.add_item(self.send_now_button)

        self.stop_button.callback = self.stop_button_handler
        self.start_button.callback = self.start_button_handler
        self.update_button.callback = self.update_button_handler
        self.send_now_button.callback = self.send_now_button_handler

    def start_task(self):
        if self.task:
            self.task.cancel()
        self.task = tasks.loop(seconds=self.interval)(self.send_message_task)
        self.task.start()

    async def send_message_task(self):
        await self.channel.send(embed=self.embed)

    async def stop_button_handler(self, interaction: disnake.MessageInteraction):
        if self.task:
            self.task.cancel()
            self.task = None
        embed = disnake.Embed(
            title="Auto-Sending Stopped",
            description="The auto-sending task has been stopped successfully.",
            color=disnake.Color.red(),
            timestamp=disnake.utils.utcnow()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def start_button_handler(self, interaction: disnake.MessageInteraction):
        if self.task and self.task.is_running():
            embed = disnake.Embed(
                title="Auto-Sending Already Running",
                description="The auto-sending task is already running.",
                color=disnake.Color.orange(),
                timestamp=disnake.utils.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.start_task()
            embed = disnake.Embed(
                title="Auto-Sending Started",
                description="The auto-sending task has been started successfully.",
                color=disnake.Color.green(),
                timestamp=disnake.utils.utcnow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def update_button_handler(self, interaction: disnake.MessageInteraction):
        def check(m):
            return m.author == interaction.author and m.channel == interaction.channel

        await interaction.response.send_message("Please enter a new interval (in seconds):", ephemeral=True)
        try:
            msg = await self.inter.bot.wait_for("message", check=check, timeout=30)
            new_interval = int(msg.content)
            if new_interval > 0:
                self.interval = new_interval
                self.start_task()
                embed = disnake.Embed(
                    title="Interval Updated",
                    description=f"Interval has been updated to {new_interval} seconds.",
                    color=disnake.Color.blurple(),
                    timestamp=disnake.utils.utcnow()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = disnake.Embed(
                    title="Invalid Interval",
                    description="Interval must be a positive integer.",
                    color=disnake.Color.red(),timestamp=disnake.utils.utcnow()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        except asyncio.TimeoutError:
            embed = disnake.Embed(
                title="Timeout Error",
                description="You took too long to respond. Please try again.",
                color=disnake.Color.red(),
                timestamp=disnake.utils.utcnow()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def send_now_button_handler(self, button: Button, interaction: disnake.MessageInteraction):
        await self.channel.send(embed=self.embed)
        embed = disnake.Embed(
            title="Message Sent",
            description="The message has been sent immediately.",
            color=disnake.Color.green(),
            timestamp=disnake.utils.utcnow()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@commands.slash_command(
    description="Start automatic message sending with interval control.",
    default_member_permissions=disnake.Permissions(moderate_members=True)
)
async def autosending(
    inter: disnake.ApplicationCommandInteraction,
    channel: disnake.TextChannel,
    title: str,
    description: str,
    interval: int,
    *,
    colors: str = commands.Param(default='green', choices=[
        'green', 'blue', 'purple', 'magenta', 'gold', 'orange', 'red', 'yellow',
    ]),
    imageurl: str = None,
    footertext: str = None,
    footericon: str = None
):
    color_map = {
        'blue': disnake.Color.blue(),
        'purple': disnake.Color.purple(),
        'magenta': disnake.Color.magenta(),
        'gold': disnake.Color.gold(),
        'orange': disnake.Color.orange(),
        'red': disnake.Color.red(),
        'yellow': disnake.Color.yellow(),
        'green': disnake.Color.green(),
    }
    if interval > 10:
        
        embed_color = color_map.get(colors, disnake.Color.green())
        embed = disnake.Embed(
            title=title,
            description=description,
            color=embed_color,
            timestamp=disnake.utils.utcnow()
        )

        if imageurl:
            embed.set_image(url=imageurl)

        if footertext:
            embed.set_footer(text=footertext, icon_url=footericon)

        view = AutoSendingView(inter, channel, embed, interval)

        embed = disnake.Embed(
            title="Auto-Sending Started",
            description="Auto-sending has been started. Use the buttons below to manage it.",
            color=disnake.Color.green(),
            timestamp=disnake.utils.utcnow()
        )
    else:
        embed = disnake.Embed(
            title="Error",
            description="The interval must be greater than 10 seconds.",
            color=disnake.Color.red()
        )
    message = await inter.response.send_message(embed=embed, view=view)
    
    await message.pin()