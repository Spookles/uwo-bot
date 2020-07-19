import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
import asyncio
import datetime
import random
import json
from pytz import timezone
from server import Server
from seaofwonders import SeaOfWonders
from unchartedwatersonline import UnchartedWatersOnline

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')
servers = {}

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:')
    for guild in bot.guilds:
        print(f'{guild.name}(id: {guild.id})')
        mainChannel = {}
        list = {}
        for channel in guild.channels:
            if channel.name == "general":
                mainChannel = channel

        if not mainChannel:
            print("Could not find a general channel for server: {}".format(guild.name))

        server = Server(guild.id, mainChannel, list)
        servers[guild.id] = server

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
        await message.channel.send("{}".format(await thanks()))
    await bot.process_commands(message)

@bot.command(brief="pong!", description="Returns the latency of the bot.")
async def ping(ctx):
    await ctx.send("Pong! Latency: **{}**seconds".format(round(bot.latency, 2)))

@bot.command(brief="", description="")
async def time(ctx):
    now_utc = datetime.datetime.now(timezone('UTC'))
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))
    await ctx.send("It is currently **{}** for the server.".format(now_pacific.strftime('%Y-%m-%d %H:%M:%S'))) 

async def thanks():
    r = random.randint(0, 8)
    if r == 0:
        return "No problem, it was my pleasure."
    elif r == 1:
        return "Considering the amount of times you've killed me... When are you gonna return the favour?"
    elif r == 2:
        return "blub"
    elif r == 3:
        return "Please give me a 5 star review on Uber."
    elif r == 4:
        return "It's quite the challenge to meet your standards. But I'm more than happy I could live up to it."
    elif r == 5:
        return "Sometimes, when I try to get a hug.. I kill people.. :( But I'm happy I have helped you :)"
    elif r == 6:
        return "You do realise you are talking to a fish.. Right?"
    elif r == 7:
        return "I have a friend called Levi, don't really see him much anymore. Well, no problem anyway. But if you see him, could you tell him I'm getting lonely?"
    else:
        return "No. Thank you!"

bot.run(TOKEN)