import discord, os, quotes, time, songgetter, redditpuller, datetime, requests
from discord.ext import commands
from dotenv import load_dotenv
from discord import FFmpegPCMAudio
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
quote = quotes.quote()
intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='~', intents=intents)

#events
@client.event
async def on_ready():
    await client.tree.sync()
    print(f'{client.user.name} is now online')
    print('---------------------')
@client.event
async def on_member_join(member):
    await member.send(f'{member} Welcome youngin ')
#commands
@client.tree.command(name = 'hello', description= 'Say hi!' )
async def hello(interaciton: discord.Interaction):
    await interaciton.response.send_message(f"Hi {interaciton.user.name}!")

@client.command()
async def goodbye(ctx):
    await ctx.send('Bye bye')

@client.tree.command(name = 'randomquote', description = 'get inspiration!')
async def randomquote(interaction: discord.Interaction):  
    await interaction.response.send_message(quote.random_quote())
@client.tree.command(name = 'joinvc', description='Use to let me a join a vc!')
async def joinvc(interaction: discord.Interaction):
    if interaction.user.fetch_voice():
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("I have connected!")
    else:
        await interaction.response.send_message('Sorry try joining a vc so i can join you')
@client.tree.command(name = 'leavevc', description = 'Use me to make me leave the vc!')
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message('I have left')
    else:
        pass
@client.tree.command(name = 'journal', description= 'Write something new!')
async def journal(interaction: discord.Interaction, entry: str):
    data ={
        "user": interaction.user.name,
        "entry": entry,
        'Date': datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')

    }
    res = requests.post('http://127.0.0.1:5000/api/journal', json = data)
    if res.ok:
        await interaction.response.send_message('It has been sent')
    else:
       await interaction.response.send_message('Please try again')
@client.command()
async def play(ctx, *music):
    song = list(music)
    songName = ' '
    for i in song:
        songName = songName + ' ' + i
    if ctx.voice_client:
        url = songgetter.search_and_download(songName)
        print(f'url:{url}')
        audio = FFmpegPCMAudio(url)
        ctx.guild.voice_client.play(audio)
    else:
        await ctx.send('poop')
@client.command() #stop music
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
@client.command() #shut down the bot
async def shut(ctx):
    await client.close()
@client.command()
async def pause(ctx):#Pause the music
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.voice_client.pause()
@client.command()
async def resume(ctx):#resume the music
    if ctx.voice_client and ctx.voice_client.is_paused():
        await ctx.voice_client.resume()
@client.command()
async def redditfeed(ctx):
    i = await redditpuller.use()
    counter = 0
    for x in i:
        if counter == 10:
            break
        else:
            counter +=1
            time.sleep(10)
            await ctx.send(x)

client.run(token)
