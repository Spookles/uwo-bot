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
from global_func import GlobalFunc

class SeaOfWonders(commands.Cog):
    """Sea of Wonders section of the bot."""
    def __init__(self, bot, servers):
        self.fishcounter = 0
        self.bot = bot
        self.cooldowns = {}
        self.checkCooldowns.start()
        self.servers = servers

    @commands.command(brief="Set your own cooldown", description="Set your cooldown by use of !cd HHMM or HH:MM\n1234 or 12:34\nTo add multiple people, or a specific person use the command as followed:\n!cd HHMM Person1 Person2 Person3 ... ... <-- Important, use spaces between the names.")
    async def cd(self, ctx, time, *args):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(ctx.guild.id)]
        channel = await GlobalFunc.getChannel(ctx.guild.channels, server.channelID)
        if re.match("^([0][0-9]|[1][0-9]|[2][0-3]):?([0-5][0-9])$", time) is not None:
            if ':' not in time:
                time = time[ : 2] + ":" + time[2 : ]
            if not args:
                server.list[ctx.author.mention] = time
                await channel.send("**{}** your cooldown is set for **{}** and that it is in **{}**".format(ctx.author.mention, time, await GlobalFunc.calculateETA(datetime.datetime.strptime(time, '%H:%M'))))
            else:
                names = ""
                for i in args:
                    server.list[i] = time
                    names+=i+", "
                names = names[:-2]
                await channel.send("Cooldown set for **{}** at **{}** and that it is in **{}**".format(names, time, await GlobalFunc.calculateETA(datetime.datetime.strptime(time, '%H:%M'))))
        else:
            await ctx.send("I'm afraid something went wrong. Use `!help cd` to see how to use the command.")
        await GlobalFunc.write(self.servers, "server_data")

    @tasks.loop(seconds=30)
    async def checkCooldowns(self):
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific')).strftime('%H:%M')
        print(now_pacific)
        for server in self.servers:
            names = []
            for i in self.servers[server].list:
                if self.servers[server].list[i] == now_pacific:
                    names.append(i)
            if names:
                await self.rm(names, self.servers[server].id, self.servers[server].channelID, False)

    async def rm(self, names, server, channel, manual):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(server)]
        channel = await GlobalFunc.getChannelFromGuild(self.bot.guilds, server)
        for i in list(server.list):
            if i in names:
                del server.list[i]
                if not manual:
                    await channel.send("**{}**, {}".format(i, await GlobalFunc.getRandomDialogue("fishing")))
                else:
                    await channel.send("Removed **{}** from cooldown list.".format(i))
        self.checkCooldowns.restart()
        await GlobalFunc.write(self.servers, "server_data")

    @commands.command(brief="Use to remove players from list", description="This command essentially does the opposite of `!cd`. You can leave out the timestamp, just have to say who you want to remove.\n!remove Person1 Person2 Person3 ... ...")
    async def remove(self, ctx, *args):
        names = []
        if not args:
            names.append(ctx.author.mention)
        else:
            names = args
        await self.rm(names, str(ctx.guild.id), self.servers[str(ctx.guild.id)].channelID, True)

    @commands.command(brief="Lists all players that have set their cooldowns", description="Shows an embed that tells you the cooldowns of everyone that is known.\nIt also shows the amount of time left till CD is finished.\nThis is all in server time, aka PDT.")
    async def list(self, ctx):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(ctx.guild.id)]
        names = ""
        cd = ""
        eta = ""

        for i in server.list:
            names+=i+"\n"
            cd+=server.list[i]+"\n"
            eta += await GlobalFunc.calculateETA(datetime.datetime.strptime(server.list[i], '%H:%M'))

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
        self.servers = await GlobalFunc.read("server_data")
        fishcounter = self.servers[str(ctx.guild.id)].fishcounter
        fishcounter = int(fishcounter)
        fishcounter += 1
        fishcounter = str(fishcounter)
        self.servers[str(ctx.guild.id)].fishcounter = fishcounter
        await ctx.send("Good job, you killed Huggles **{}** times".format(fishcounter))
        await GlobalFunc.write(self.servers, "server_data")