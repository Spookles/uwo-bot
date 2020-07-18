import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
import asyncio
from seaofwonders import SeaOfWonders
from unchartedwatersonline import UnchartedWatersOnline

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    bot.add_cog(UnchartedWatersOnline(bot))
    bot.add_cog(SeaOfWonders(bot))
    for guild in bot.guilds:
        print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

@bot.event
async def on_message(message):
    if "thanks huggles" in message.content.lower():
        await message.channel.send("No problem, it was my pleasure.")
    await bot.process_commands(message)

@bot.command(brief="pong!", description="Returns the latency of the bot.")
async def ping(ctx):
    await ctx.send("Pong! Latency: **{}**seconds".format(round(bot.latency, 2)))

bot.run(TOKEN)