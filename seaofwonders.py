import discord
import asyncio
import re
from datetime import datetime
from pytz import timezone
from discord.ext import tasks, commands

class SeaOfWonders(commands.Cog):
    """Sea of Wonders section of the bot."""
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    @commands.command(brief="", description="")
    async def cd(self, ctx, time):
        if re.match("^([0-9]|0[0-9]|1[0-9]|2[0-3]):?[0-5][0-9]$", time) is not None:
            if ':' not in time:
                time = time[ : 2] + ":" + time[2 : ]
            self.cooldowns[ctx.author.display_name] = time
            await ctx.send("**{}** your cooldown is set for **{}**".format(ctx.author.display_name, time))
        else:
            await ctx.send("I'm afraid the time you put in is not in the correct format.\nPlease use 'HH:MM' **or** 'HHMM'.")

    @commands.command(brief="", description="")
    async def list(self, ctx):
        names = ""
        cd = ""
        eta = ""

        now_utc = datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific'))  

        for i in self.cooldowns:
            names+=i+"\n"
            cd+=self.cooldowns[i]+"\n"
            date_time_obj = datetime.strptime(self.cooldowns[i], '%H:%M')
            now_pacific = now_pacific.replace(tzinfo=None)
            diff = date_time_obj - now_pacific
            minute = diff.seconds//60%60
            hour = diff.seconds//3600
            eta+=f"{hour:02}:{minute:02}"+"\n"

        embed=discord.Embed(title="Cooldown(s)", description="Everyone their known cooldown(s)", color=0x00d9ff)
        embed.add_field(name="Name", value="{}".format(names), inline=True)
        embed.add_field(name="CD", value="{}".format(cd), inline=True)
        embed.add_field(name="Time Left", value="{}".format(eta), inline=True)
        await ctx.send(embed=embed)
