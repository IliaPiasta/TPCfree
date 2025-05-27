import disnake
from disnake.ext import commands
from pytube import Search
import random
from .additonal import g, get_random_video, topics, topics_ru,topics_ua, topics_es, topics_de, topic_zh, github, trans, language_choices, languages, x, jokes, brawlify_club, teacher_jokes, generate, get_movie_details, censor_and_check
id_ = [1173042124707598346, 1149711163676954684]

class CopyButton(disnake.ui.View):
    def __init__(self, text: str):
        super().__init__(timeout=2592000)
        self.text = text
        
    @disnake.ui.button(label=f"Copy", style=disnake.ButtonStyle.secondary)
    async def copy_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_message(f"```{self.text}```", ephemeral=True)
        
class GetButton(disnake.ui.View):
    def __init__(self, text: str):
        super().__init__(timeout=2592000)
        self.text = text
        
    @disnake.ui.button(label=f"Get", style=disnake.ButtonStyle.secondary)
    async def copy_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_message(f"{self.text}", ephemeral=True)
        
@commands.slash_command(description='Find movie details by title')
async def findmovie(ctx, movie_title: str):
    movie_data = get_movie_details(trans(text=movie_title, language='en'))
    
    try:
        embed = disnake.Embed(
            title=movie_title,
            description=f"**{movie_data['Plot']}**",
            color=disnake.Color.dark_green()
        )
        
        embed.set_image(url=movie_data['Poster'])
        
        ratings_text = "\n".join([f"**{rating['Source']}**: {rating['Value']}" for rating in movie_data['Ratings']])
        
        embed.add_field(name='⭐ **Ratings**', value=ratings_text, inline=True)
        embed.add_field(name='🖼️ **Poster**', value=f"[**Click to view poster**]({movie_data['Poster']})", inline=True)
        
        embed.set_footer(text="The magic of movies never fades...", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Film_reel.svg/1200px-Film_reel.svg.png")
        
    except KeyError:
        embed = disnake.Embed(
            title="Movie Not Found",
            description=f"Sorry, we couldn't find any information for the movie: **{movie_title}**",
            color=disnake.Color.red(),
        )
        
    await ctx.send(embed=embed)
        
@commands.slash_command(description="Merry christmas(gif)")
async def happy(ctx):
    embed = disnake.Embed(
            title=f"Happy New Year",
            description=f"**2025 dude**",
            color=disnake.Color.blue(),
        )
    
    embed.set_image(url='https://media.tenor.com/cHXf2CRshxAAAAAM/new-year.gif')
    await ctx.send(embed = embed)
        
@commands.slash_command(
    description="Generate images based on the parameters you provide.",
    name='artwork'
)
async def artgen(
    ctx,
    prompt: str,
    style_preset: str = commands.Param(
        choices=[
            '3d-model', 'analog-film', 'anime', 'cinematic', 'comic-book', 
            'digital-art', 'enhance', 'fantasy-art', 'isometric', 'line-art', 
            'low-poly', 'neon-punk', 'origami', 'photographic', 'pixel-art', 
            'texture', 'craft-clay'
        ], default='photographic'
    ),
    size: str = commands.Param(default='1:1', choices=['1:1', '16:9', '4:3', '21:9'])
):
    await ctx.response.defer()

    # Определение размеров изображения на основе выбранного соотношения
    width, height = 512, 512  # По умолчанию 1:1
    if size == '16:9':
        width, height = 1024, 576
    elif size == '4:3':
        width, height = 1024, 768
    elif size == '21:9':
        width, height = 1024, 439

    try:
        # Генерация изображения и получение ссылки
        new_prompt, checked = censor_and_check(trans(text=prompt, language='en'))
        print(checked)
        if checked == False:
            generated_image_url = generate(prompt=new_prompt, style_preset=style_preset, width=width, height=height)
        else:
            generated_image_url = 'https://media.gq.com/photos/5bd8ab9917c41d3a0551d6d3/16:9/w_2560%2Cc_limit/Tired-All-the-Time.gif'
            new_prompt += ' **Message blocked**'
        if not generated_image_url:
            raise ValueError("Failed to generate image URL.")

        embed = disnake.Embed(
            title=f"Style: {style_preset.capitalize()} {size}",
            description=f"-# **Prompt:** ```{new_prompt}```",
            color=disnake.Color.blurple(),
        )
        embed.set_image(url=generated_image_url)
        embed.set_footer(text="Art generated based on your input!")

        view = CopyButton(generated_image_url)
        await ctx.edit_original_message(embed=embed, view=view)

    except Exception as e:
        await ctx.edit_original_message(content=f"An error occurred: {e}")

@commands.slash_command(description="Find Youtube(video) for your topic")
async def video(ctx, topic):
    search = Search(topic)
    videos = search.results[:1]

    if videos:
        for video in videos:
            
            if ctx.guild is None: 
                await ctx.send(f"{video.title}: {video.watch_url}" + '\n-# You can always add our bot to your Discord server to get more features.')
            else: 
                if ctx.guild.id in id_:  
                    await ctx.send('This command is disabled. You can use it on other servers or in direct messages.')
                else:
                   await ctx.send(f"{video.title}: {video.watch_url}")
    else:
        await ctx.send("Oh we not find it")
        
@commands.slash_command(description="Random Video(Youtube)")    
async def random_video(ctx, query: str = None, *, language: str = commands.Param(default='eng', choices=['eng', 'ru', 'ua', 'es', 'de', 'zh'])):
    if query is None:
        topics_dict = {
            'eng': topics,
            'ru': topics_ru,
            'ua': topics_ua,
            'es': topics_es,
            'de' : topics_de,
            'zh' : topic_zh
            
            
        }
        
        query = random.choice(topics_dict.get(language, topics))
    
    video = await get_random_video(query)

    if not video:
        await ctx.send("No videos found for this topic.")
        return


    
    if ctx.guild is None: 
        await ctx.send(f'Topic: {query}\n{video.watch_url}' + '\n-# You can always add our bot to your Discord server to get more features.')
    else: 
        if ctx.guild.id in id_:  
            await ctx.send('This command is disabled. You can use it on other servers or in direct messages.')
        else:
            await ctx.send(f'Topic: {query}\n{video.watch_url}')
    
        
@commands.slash_command(description="Search information on the website")
async def google(ctx: disnake.ApplicationCommandInteraction, search: str):
    search_result = g(search)
    
    embed = disnake.Embed(
        title="🔍 Search Result",
        description=f"Here are the results for your search: ",
        color=disnake.Color.blue()
    )
    embed.add_field(name="Search Result", value=search_result, inline=False)
    view = GetButton(search_result)
    await ctx.send(search_result, embed=embed, view=view)
    
@commands.slash_command(description="Search GitHub repositories for name")
async def github_find(ctx: disnake.ApplicationCommandInteraction, search: str):
    result = github(search)
    embed = disnake.Embed(
        title="🔍 GitHub Repository Search",
        description=f"Results for your search: **{search}**",
        color=disnake.Color.blue()
    )
    embed.add_field(name="Repositories", value=result, inline=False)
    view = GetButton(result)
    await ctx.send(embed=embed, view=view)

@commands.slash_command(description="Translate your message to another language")
async def translate(inter: disnake.ApplicationCommandInteraction, text: str, language: str = commands.Param(choices=language_choices)):
    code = next(code for name, code in languages.items() if f"{name} ({code})" == language)
    translated_text = trans(text, code)
    
    embed = disnake.Embed(
        title="🌐 Translation",
        description=f"Original Text:\n{text}\n\nTranslated Text:\n{translated_text}",
        color=disnake.Color.green()
    )
    
    view = CopyButton(translated_text)
    
    await inter.response.send_message(embed=embed, view=view)

@commands.slash_command(description="Find people on Twitter (or X)")
async def twitter(ctx: disnake.ApplicationCommandInteraction, search: str):
    result = x(search)
    embed = disnake.Embed(
        title="🔍 Twitter/X Search",
        description=f"Results for your search: **{search}**",
        color=disnake.Color.blue()
    )
    embed.add_field(name="Profiles", value=result, inline=False)
    
    view = GetButton(result)
    
    await ctx.send(embed=embed, view=view)
    
# @commands.slash_command(description="Remaid me, something")
# async def remindme(ctx: disnake.ApplicationCommandInteraction, message: str, duration:str):
#     timeout_duration  = parse_time(duration)

@commands.slash_command(description="Heads or Tails 50/50")
async def flipcoin(ctx: disnake.ApplicationCommandInteraction):
    result = random.choice(["Heads", "Tails"])
    embed = disnake.Embed(
        title="🪙 Flip Coin",
        description=f"The coin landed on: **{result}**",
        color=disnake.Color.gold()
    )
    view = GetButton(result)
    await ctx.send(embed=embed, view=view)
    
# Command to get a random dad joke
@commands.slash_command(description="Get a random dad joke")
async def dadjoke(inter: disnake.ApplicationCommandInteraction):
    joke = random.choice(jokes)
    
    embed = disnake.Embed(
        title="Dad Joke",
        description=joke,
        color=disnake.Color.orange()
    )
    await inter.response.send_message(embed=embed)
    
# Command to get a random teacher joke
@commands.slash_command(description="Get a random teacher joke")
async def teacherjoke(inter: disnake.ApplicationCommandInteraction):
    joke = random.choice(teacher_jokes)
    
    embed = disnake.Embed(
        title="teacher Joke",
        description=joke,
        color=disnake.Color.orange()
    )
    await inter.response.send_message(embed=embed)
    
@commands.slash_command(description="Find your Brawl club ")
async def clubfinder(inter: disnake.ApplicationCommandInteraction, clubid : str):
    result = brawlify_club(clubid)
    embed = disnake.Embed(
        title="Brawl Stars Club",
        description= f"Club {clubid}\n" + f"🔗 [View]({result})",
        color=disnake.Color.yellow()
    )
    view = GetButton(result)
    await inter.response.send_message(embed=embed, view=view)

# not done

# @bot.slash_command(description="Get random mem")
# async def reddit(inter: disnake.ApplicationCommandInteraction, count: int = 1):
#     memes = await get_reddit_memes(count)
#     meme_text = ""
#     for meme in memes:
#         meme_text += f"{meme['title']}\n{meme['url']}\n"
#     await inter.response.send_message(meme_text)
    
