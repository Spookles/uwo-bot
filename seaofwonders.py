import discord
import asyncio
import re
import threading
import time
import datetime
import random
import json
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

    @tasks.loop(seconds=30)
    async def checkCooldowns(self):
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific')).strftime('%H:%M')
        names = []
        for i in self.cooldowns:
            if self.cooldowns[i] == now_pacific:
                names.append(i)
        if names:
            await self.rm(names, False)

    async def rm(self, names, manual):
        for i in list(self.cooldowns):
            if i in names:
                del self.cooldowns[i]
                if not manual:
                    await self.ctx.send("**{}**, {}".format(i, await self.return_to_fishing()))
                else:
                    await self.ctx.send("Removed **{}** from cooldown list.".format(i))
        self.checkCooldowns.restart()

    @commands.command(brief="Use to remove players from list", description="This command essentially does the opposite of `!cd`. You can leave out the timestamp, just have to say who you want to remove.\n!remove Person1 Person2 Person3 ... ...")
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

    @staticmethod
    async def return_to_fishing():
        r = random.randint(0, 10)
        if r == 0:
            return "I'm pleased to announce, you can go back _trying_ to kill me."
        elif r == 1:
            return "goodluck trying to spawn me again."
        elif r == 2:
            return "back to fishing!"
        elif r == 3:
            return "you know the definition of insanity? Oh well, you can try again if you'd like."
        elif r == 4:
            return "you're welcome back into my lair."
        elif r == 5:
            return "🔔🔔🔔 IT IS TIME."
        elif r == 4:
            return "grab your friends and try me, _bitch_."
        elif r == 6:
            return "have fun in the Sea of Wonders."
        elif r == 7:
            return "https://www.youtube.com/watch?v=tkzY_VwNIek"
        elif r == 8:
            return "will I turn into 🍣 this time?"
        elif r == 9:
            return "good thing my species have a great fertility rate."
        else:
            return "🎣 you know what that means."