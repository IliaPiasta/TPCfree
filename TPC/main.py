import disnake
from disnake.ext import commands, tasks
# *TOKEN
from TPC.commands.core.main import video, findmovie, random_video, google, github_find, translate, twitter, flipcoin, dadjoke, teacherjoke, clubfinder, artgen, happy
from commands.moderation import deafen, undeafen, massmove, send, say, call, notifyall, warn, clear, kick, report, mute, unmute, ban, unban, addrank, delrank, ranks, roleinfo, temprole, autosending, RoleMenuCog
# from commands.main.vs import join, leave, play

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready!")


id_ = [1173042124707598346, 1149711163676954684]

#funny 
bot.add_slash_command(video)
bot.add_slash_command(random_video)
bot.add_slash_command(google)
bot.add_slash_command(github_find)
bot.add_slash_command(translate)
bot.add_slash_command(twitter)
bot.add_slash_command(flipcoin)
bot.add_slash_command(dadjoke)
bot.add_slash_command(teacherjoke)
bot.add_slash_command(clubfinder)
bot.add_slash_command(happy)
bot.add_slash_command(findmovie)

#moders - vs
bot.add_slash_command(deafen)
bot.add_slash_command(undeafen)
bot.add_slash_command(massmove)
#moders - ls 
bot.add_slash_command(send)
bot.add_slash_command(say)
bot.add_slash_command(call)
bot.add_slash_command(notifyall)
bot.add_slash_command(warn)
# role menu
bot.add_cog(RoleMenuCog(bot))
#moders - main 
bot.add_slash_command(clear)
bot.add_slash_command(kick)
bot.add_slash_command(report)
bot.add_slash_command(mute)
bot.add_slash_command(unmute)
bot.add_slash_command(ban)
bot.add_slash_command(unban)
#moders - ranks 
bot.add_slash_command(addrank)
bot.add_slash_command(delrank)
bot.add_slash_command(ranks)
bot.add_slash_command(roleinfo)
bot.add_slash_command(temprole)
# auto 
bot.add_slash_command(autosending)
# AI
bot.add_slash_command(artgen)
    
    
user_message_times = {}   
@bot.slash_command(description="Get help information")
async def help(interaction: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        title="📚 Help Information",
        description="Need help? Use the buttons below to get more information.",
        color=disnake.Color.blue()
    )
    view = disnake.ui.View()

    commands_button = disnake.ui.Button(
        label="All Commands",
        url="https://iliapiasta.github.io/TcP/pages/commands.html",
        style=disnake.ButtonStyle.link
    )
    support_button = disnake.ui.Button(
        label="Support Server",
        url="https://discord.com/channels/1242558139262435328/1275577431658594356",
        style=disnake.ButtonStyle.link
    )

    view.add_item(commands_button)
    view.add_item(support_button)

    await interaction.response.send_message(embed=embed, view=view)

@bot.slash_command(name="invite", description="Send an invite link for TPC BOT.")
async def invite(interaction: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        title="🚀 Invite TPC BOT",
        description="Want to add TPC BOT to your server? Click the button below to get the invite link.",
        color=disnake.Color.green()
    )
    view = disnake.ui.View()

    invite_button = disnake.ui.Button(
        label="Invite TPC BOT",
        url="https://discord.com/oauth2/authorize?client_id=1196199588558819449&permissions=8&scope=bot+applications.commands",
        style=disnake.ButtonStyle.link
    )
    support_button = disnake.ui.Button(
        label="Support Server",
        url="https://discord.com/channels/1242558139262435328/1275577431658594356",
        style=disnake.ButtonStyle.link
    )

    view.add_item(invite_button)
    view.add_item(support_button)

    await interaction.response.send_message(embed=embed, view=view)
    
# Command to get bot info
@bot.slash_command(description="Get information about the bot")
async def info(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        title="Yo, I'm TpC #6216!",
        description=(
            "Your friendly neighborhood bot,\n"
            "here to help you out (and maybe crack a joke or two).\n"
            "Whether you need a hand, a random fact, or just a good laugh, I've got you covered!\n"
            "Need to spice up your server? Add me, and let's make this place awesome together!\n"
            "Oh, and did I mention? I'm pretty good at memes too."
        ),
        color=disnake.Color.purple()
    )
    await inter.response.send_message(embed=embed)

bot.run(TOKEN)
