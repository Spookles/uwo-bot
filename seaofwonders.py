import discord
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
                name = ctx.author.mention
                name = name.replace("!", "")
                server.list[name] = time
                await channel.send("**{}** your cooldown is set for **{}** and that it is in **{}**".format(ctx.author.display_name, time, await GlobalFunc.calculateETA(datetime.datetime.strptime(time, '%H:%M'))))
            else:
                names = ""
                for i in args:
                    if "@" in i:
                        i = i.replace("!", "")
                        server.list[i] = time
                        names+="{}, ".format(await GlobalFunc.getDisplayName(ctx.guild, i))
                    else:
                        server.list[i] = time
                        names+="{}, ".format(i)
                names = names[:-2]
                await channel.send("Cooldown set for **{}** at **{}** and that it is in **{}**".format(names, time, await GlobalFunc.calculateETA(datetime.datetime.strptime(time, '%H:%M'))))
        else:
            await ctx.send("I'm afraid something went wrong. Use `!help cd` to see how to use the command.")
        await GlobalFunc.write(self.servers, "server_data")

    @tasks.loop(seconds=60)
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
                await self.rm(names, "0", self.servers[server].id, self.servers[server].channelID, False)

    async def rm(self, names, index, server, channel, manual):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(server)]
        channel = await GlobalFunc.getChannelFromGuild(self.bot.guilds, server)
        removeList = ""
        guild = self.bot.get_guild(int(server.id))
        count = 1
        for i in list(server.list):
            if int(index) != 0 and count == int(index):
                if "@" in i:
                    removeList += "{} ".format(await GlobalFunc.getDisplayName(guild, i))
                    del server.list[i]
                else:
                    removeList += "{} ".format(i)
                    del server.list[i]
            if i in names:
                if "@" in i:
                    i = i.replace("!", "")
                    removeList += "{} ".format(await GlobalFunc.getDisplayName(guild, i))
                    del server.list[i]
                else:
                    removeList += "{} ".format(i)
                    del server.list[i]
            count+=1
        removeList = removeList[:-1]
        if (not manual) and removeList:
            await channel.send("**{}**, {}".format(removeList, await GlobalFunc.getRandomDialogue("fishing")))
        elif removeList:
            await channel.send("Removed **{}** from cooldown list.".format(removeList))
        await GlobalFunc.write(self.servers, "server_data")

    @commands.command(brief="Use to remove players from list", description="This command essentially does the opposite of `!cd`. You can leave out the timestamp, just have to say who you want to remove.\n!remove Person1 Person2 Person3 ... ...")
    async def remove(self, ctx, *args):
        self.servers = await GlobalFunc.read("server_data")
        names = []
        newNames = []
        rmIndex = "0"
        if not args:
            newNames.append(ctx.author.mention.replace("!", ""))
        elif re.match("^([0-9]|[0-9][0-9])$", str(args[0])):
            rmIndex = str(args[0])
        else:
            names = args
        for n in names:
            newNames.append(n.replace("!", ""))
        await self.rm(newNames, rmIndex, str(ctx.guild.id), self.servers[str(ctx.guild.id)].channelID, True)

    @commands.command(brief="Lists all players that have set their cooldowns", description="Shows an embed that tells you the cooldowns of everyone that is known.\nIt also shows the amount of time left till CD is finished.\nThis is all in server time, aka PDT.")
    async def list(self, ctx):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(ctx.guild.id)]
        index = ""
        names = ""
        cd = ""
        eta = ""

        count = 1
        for i in server.list:
            index+="{}\n".format(count)
            names+=i+"\n"
            cd+=server.list[i]+"\n"
            eta += await GlobalFunc.calculateETA(datetime.datetime.strptime(server.list[i], '%H:%M'))
            count+=1

        if not index:
            index = "0"
        if not names:
            names = "none"
        if not cd:
            cd = "none"
        if not eta:
            eta = "none"

        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific'))  

        embed=discord.Embed(title="Cooldown(s)", description="", color=0x252525)
        embed.set_footer(text="{} PDT day ends in {}".format(now_pacific.strftime('%Y-%m-%d %H:%M'), await GlobalFunc.calculateETA(datetime.datetime.strptime("00:00", '%H:%M'))))
        embed.add_field(name="Index", value="{}".format(index), inline=True)
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

    @commands.command(brief="", description="")
    async def how(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0xff0000))

        embed.set_author(name="How To Use Huggles")
        embed.add_field(name="The Basic Commands", value="And how to use them")
        embed.add_field(name="!cd", value="**!cd HHMM Name Name ...** \nTime can be set as 1234 or 12:34. Important is that it's always 4 digits! So 6:34 would be 06:34.\nNames **must** always be seperated by spaces.\n\nQuick use: **!cd HHMM**\nThis will only add yourself.", inline=False)
        embed.add_field(name="!list", value="List shows all the cooldowns of people that are registered. And when they run out.", inline=False)
        embed.add_field(name="!remove", value="You can remove yourself or others by doing **!remove Name Name ...**\nAgain names **must** be seperated by spaces.\nYou will automatically be removed from **!list** when your cooldown is over. You will also be notified when that happens.\n\nQuick use: **!remove**\nThis will only remove yourself.", inline=False)

        await ctx.send(embed=embed)