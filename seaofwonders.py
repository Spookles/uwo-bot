import discord
import re
import threading
import time
import datetime
import random
import json
import operator
from pytz import timezone
from discord.ext import tasks, commands
from global_func import GlobalFunc
from user import User, addUser, removeCharacters

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
            try:
                if ':' not in time:
                    time = time[ : 2] + ":" + time[2 : ]
                if not args:
                    i = removeCharacters(str(ctx.author.id))
                    name = ctx.author.mention
                    name = name.replace("!", "")
                    server.list[name] = time
                    if i not in server.users:
                        server = addUser(server, i)
                        server.users[removeCharacters(i)].increment()
                    else:
                        server.users[removeCharacters(i)].increment()                    
                    await ctx.message.add_reaction("✅")
                else:
                    names = ""
                    for i in args:
                        if "@" in i and "<" in i:
                            i = i.replace("!", "")
                            server.list[i] = time
                            names+="{}, ".format(str(i))
                            if removeCharacters(i) not in server.users:
                                server = addUser(server, i)
                                server.users[removeCharacters(i)].increment()
                            else:
                                server.users[removeCharacters(i)].increment()
                        else:
                            server.list[i] = time
                            names+="{}, ".format(i)
                    names = names[:-2]
                    await ctx.message.add_reaction("✅")
            except Exception as e:
                print(e)
                await channel.send("<@154332161737097217> Error: {}".format(e))
                await ctx.message.add_reaction("⛔")
        else:
            await ctx.send("I'm afraid something went wrong. Use `!help cd` to see how to use the command.")
        await GlobalFunc.write(self.servers, "server_data")

    @tasks.loop(seconds=30)
    async def checkCooldowns(self):
        try:
            now_utc = datetime.datetime.now(timezone('UTC'))
            now_pacific = now_utc.astimezone(timezone('US/Pacific')).strftime('%H:%M')
            stream = discord.Streaming(name=now_utc.astimezone(timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M'), url="https://www.twitch.tv/dspookles")
            await self.bot.change_presence(activity=stream)
            print(now_pacific)
            for server in self.servers:
                names = []
                for i in self.servers[server].list:
                    if self.servers[server].list[i] == now_pacific:
                        names.append(i)
                if names:
                    await self.rm(names, "0", self.servers[server].id, self.servers[server].channelID, False, None)

        except Exception as e: print(e)

    async def rm(self, names, index, server, channel, manual, ctx):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(server)]
        channel = await GlobalFunc.getChannelFromGuild(self.bot.guilds, server)
        removeList = ""
        addList = ""
        guild = self.bot.get_guild(int(server.id))
        count = 1
        for i in list(server.list):
            try:
                if int(index) != 0 and count == int(index):
                    if "@" in i and "<" in i:
                        removeList += "{} ".format(str(i))
                        del server.list[i]
                    else:
                        removeList += "{} ".format(i)
                        del server.list[i]
                if i in names:
                    if "@" in i and "<" in i:
                        i = i.replace("!", "")
                        removeList += "{} ".format(str(i))
                        addList += "{} ".format(i)
                        del server.list[i]
                    else:
                        removeList += "{} ".format(i)
                        addList += "{} ".format(i)
                        del server.list[i]
            except Exception as e:
                if ctx:
                    print(e)
                    await channel.send("<@154332161737097217> Error: {}".format(e))
                    await ctx.message.add_reaction("⛔")
            count+=1
        removeList = removeList[:-1]
        addList = addList[:-1]
        if (not manual) and removeList:
            await channel.send("**{}**, {}".format(addList, await GlobalFunc.getRandomDialogue("fishing")))
        elif removeList:
            await ctx.message.add_reaction("✅")
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
        await self.rm(newNames, rmIndex, str(ctx.guild.id), self.servers[str(ctx.guild.id)].channelID, True, ctx)

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
            names+="{}: {}\n".format(count, i)
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
        embed.add_field(name="Index: Name", value="{}".format(names), inline=True)
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
    async def levisteak(self, ctx):
        self.servers = await GlobalFunc.read("server_data")
        levicounter = self.servers[str(ctx.guild.id)].levicounter
        levicounter = int(levicounter)
        levicounter += 1
        levicounter = str(levicounter)
        self.servers[str(ctx.guild.id)].levicounter = levicounter
        await ctx.send("Good job, you killed Princess Elsa **{}** times".format(levicounter))
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

    @commands.command(brief="", description="")
    async def server(self, ctx):
        self.servers = await GlobalFunc.read("server_data")
        totalruns = 0;
        totalplayers = 0;
        peopleInServer = ctx.guild.member_count
        for user in self.servers[str(ctx.guild.id)].users:
            totalruns += self.servers[str(ctx.guild.id)].users[user].runs
            totalplayers += 1

        embed = discord.Embed(title="All the information of this server!", description="Containing all runs from SoW, Huggles, Princess Elsa etc.", color=0x00ffcc)
        embed.add_field(name="Everyone their runs combined", value="{} roughly {} runs".format(totalruns, round((totalruns/5))), inline=True)
        embed.add_field(name="Fishers", value="{}/{}".format(totalplayers, peopleInServer), inline=True)
        embed.add_field(name="Fishing data", value="_you murderers_", inline=False)
        embed.add_field(name="Fishsticks", value=self.servers[str(ctx.guild.id)].fishcounter, inline=True)
        embed.add_field(name="Levisteaks", value=self.servers[str(ctx.guild.id)].levicounter, inline=True)
        await ctx.send(embed=embed)

    @commands.command(brief="", description="")
    async def profile(self, ctx, *args):
        self.servers = await GlobalFunc.read("server_data")
        r = random.randint(0, 0xffffff)

        if not args:
            try:
                embed = discord.Embed(colour=discord.Colour(r))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_author(name=ctx.author.display_name)

                embed.add_field(name="Sow Runs", value=self.servers[str(ctx.guild.id)].users[removeCharacters(str(ctx.author.id))].runs, inline=True)
            except KeyError:
                embed.add_field(name="Sow Runs", value='0', inline=True)

        else:
            member = await ctx.guild.fetch_member(int(removeCharacters(args[0])))
            try:
                self.servers = await GlobalFunc.read("server_data")
                embed = discord.Embed(colour=discord.Colour(r))
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name=member.display_name)

                embed.add_field(name="SoW Runs", value=self.servers[str(ctx.guild.id)].users[removeCharacters(str(args[0]))].runs, inline=True)
            except KeyError:
                embed.add_field(name="SoW Runs", value='0', inline=True) 
        await ctx.send(embed=embed)

    @commands.command(brief="", description="")
    async def leaderboard(self, ctx):
        self.servers = await GlobalFunc.read("server_data")
        server = self.servers[str(ctx.guild.id)]
        leaderboard = {}
        index = 0
        for user in (sorted(server.users.values(), key=operator.attrgetter('runs'), reverse=True)):
            leaderboard[index] = user
            index+=1
            if index == 10:
                break;
        
        names = ""
        runs = ""
        count = 1
        for i in leaderboard:
            names+="{}: <@{}>\n".format(count, leaderboard[i].id)
            runs+="{}\n".format(leaderboard[i].runs)
            count+=1

        embed=discord.Embed(title="Sea of Wonders leaderboard", description="", color=0x252525)
        embed.add_field(name="Index: Name", value="{}".format(names), inline=True)
        embed.add_field(name="Runs", value="{}".format(runs), inline=True)
        await ctx.send(embed=embed)

        await GlobalFunc.write(self.servers, "server_data")