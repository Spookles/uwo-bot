import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
import datetime
import random
import json
from pytz import timezone
from server import Server
from user import User
from global_func import GlobalFunc
from seaofwonders import SeaOfWonders
from unchartedwatersonline import UnchartedWatersOnline

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='#')
servers = {}
dialogue = {}

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:')
    for guild in bot.guilds:
        print(f'{guild.name}(id: {guild.id})')
        mainChannel = {}
        list = {}
        users = {}
        for channel in guild.channels:
            if channel.name == "general":
                mainChannel = channel

        if not mainChannel:
            print("Could not find a general channel for server: {}".format(guild.name))

        server = Server(str(guild.id), mainChannel.id, list, users)
        servers[guild.id] = server
    if not os.path.exists("server_data.json"):
        await GlobalFunc.write(servers, "server_data")
    if not os.path.exists("dialogue.json"):
        await GlobalFunc.write(dialogue, "dialogue")
    bot.add_cog(UnchartedWatersOnline(bot))
    bot.add_cog(SeaOfWonders(bot, servers))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

@bot.event
async def on_message(message):
    if "thanks huggles" in message.content.lower():
        await message.channel.send("{}".format(await GlobalFunc.getRandomDialogue("thanks")))
    await bot.process_commands(message)

@bot.command(brief="pong!", description="Returns the latency of the bot.")
async def ping(ctx):
    await ctx.send("Pong! Latency: **{}**seconds".format(round(bot.latency, 2)))

@bot.command(brief="", description="")
async def tail(ctx, name=None):
    if name:
        await ctx.send("{}, {}".format(name, await GlobalFunc.getRandomDialogue("tail")))
    else:
        await ctx.send("Who did you want me to punish {}?".format(ctx.author.mention))

@bot.command(brief="", description="")
async def time(ctx):
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))
    await ctx.send("It is currently **{}** for the server.".format(now_pacific.strftime('%Y-%m-%d %H:%M:%S'))) 

@bot.command(brief="", description="")
async def debug(ctx):
    await ctx.send("```json\n {}``` You can give it a readable format at: https://jsonformatter.curiousconcept.com/. Make sure to have dev mode turned on in Discord to be able to copy IDs. This server ID is: **{}**.".format(await GlobalFunc.raw("server_data"), ctx.guild.id))

@bot.command(brief="", description="")
async def coin(ctx):
    r = random.randint(0, 1)
    if r == 1:
        await ctx.send("Heads!")
    else:
        await ctx.send("Tails!")

@bot.command(brief="", description="")
async def roll(ctx, arg):
    if int(arg) <= 99999:
        try:
            r = random.randint(0, int(arg))
            if r == 69:
                await ctx.send(str(r)+' nice')
            else:
                await ctx.send(str(r))
        except (ValueError, UnboundLocalError):
            await tail(ctx, ctx.author.display_name)

bot.run(TOKEN)
