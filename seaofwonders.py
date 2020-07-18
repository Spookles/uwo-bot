import discord
import asyncio
import re
import threading
import time
import datetime
from pytz import timezone
from discord.ext import tasks, commands

class SeaOfWonders(commands.Cog):
    """Sea of Wonders section of the bot."""
    def __init__(self, bot):
        self.fishcounter = 0
        self.bot = bot
        self.cooldowns = {}
        self.checkCooldowns.start()
        self.ctx = {}

    @commands.command(brief="Set your own cooldown", description="Set your cooldown by use of !cd HHMM or HH:MM\n1234 or 12:34\nTo add multiple people, or a specific person use the command as followed:\n!cd HHMM Person1 Person2 Person3 ... ... <-- Important, use spaces between the names.")
    async def cd(self, ctx, time, *args):
        self.ctx = ctx
        if re.match("^([0][0-9]|[1][0-9]|[2][0-3]):?([0-5][0-9])$", time) is not None:
            if ':' not in time:
                time = time[ : 2] + ":" + time[2 : ]
            if not args:
                self.cooldowns[ctx.author.display_name] = time
                await ctx.send("**{}** your cooldown is set for **{}**".format(ctx.author.display_name, time))
            else:
                names = ""
                for i in args:
                    self.cooldowns[i] = time
                    names+=i+", "
                names = names[:-2]
                await ctx.send("Cooldown set for **{}** at **{}**".format(names, time))
        else:
            await ctx.send("I'm afraid something went wrong. Use `!help cd` to see how to use the command.")

    @tasks.loop(minutes=1.0)
    async def checkCooldowns(self):
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific')).strftime('%H:%M')
        print(now_pacific)
        names = []
        for i in self.cooldowns:
            if self.cooldowns[i] == now_pacific:
                names.append(i)
        if names:
            await self.rm(names, False)

    async def rm(self, names, manual):
        index = 0
        for i in list(self.cooldowns):
            if i == names[index]:
                del self.cooldowns[i]
                index+=1
                if not manual:
                    await self.ctx.send("**{}** your cooldown is finished, back to fishing!".format(i))
                else:
                    await self.ctx.send("Removed **{}** from cooldown list.".format(i))
        self.checkCooldowns.restart()

    @commands.command(brief="", description="")
    async def remove(self, ctx, *args):
        names = []
        if not args:
            names.append(ctx.author.display_name)
        else:
            names = args
        await self.rm(names, True)

    @commands.command(brief="Lists all players that have set their cooldowns", description="Shows an embed that tells you the cooldowns of everyone that is known.\nIt also shows the amount of time left till CD is finished.\nThis is all in server time, aka PDT.")
    async def list(self, ctx):
        names = ""
        cd = ""
        eta = ""

        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific'))  

        for i in self.cooldowns:
            names+=i+"\n"
            cd+=self.cooldowns[i]+"\n"
            date_time_obj = datetime.datetime.strptime(self.cooldowns[i], '%H:%M')
            now_pacific = now_pacific.replace(tzinfo=None)
            diff = date_time_obj - now_pacific
            minute = diff.seconds//60%60
            hour = diff.seconds//3600
            eta+=f"{hour:02}:{minute:02}"+"\n"

        if not names:
            names = "none"
        if not cd:
            cd = "none"
        if not eta:
            eta = "none"

        embed=discord.Embed(title="Cooldown(s)", description="Everyone their known cooldown(s) in PDT server time", color=0x00d9ff)
        embed.add_field(name="Name", value="{}".format(names), inline=True)
        embed.add_field(name="CD", value="{}".format(cd), inline=True)
        embed.add_field(name="Time Left", value="{}".format(eta), inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(brief="", description="")
    async def fishsticks(self, ctx):
        self.fishcounter+=1
        await ctx.send("Good job, you killed Huggles **{}** times".format(self.fishcounter))