import discord
from discord.ext import tasks, commands
import jsonpickle
import random
import datetime
from pytz import timezone

class GlobalFunc():
    """Functions that get used by multiple cogs."""

    @staticmethod
    async def write(obj, filename):
        """Write an object to a json file with the given filename."""
        filename+=".json"
        f = open(filename, 'w')
        json_obj = jsonpickle.encode(obj)
        f.write(json_obj)
        f.close()

    @staticmethod
    async def read(filename):
        """Read an object from a json file and return it as an object."""
        filename+=".json"
        f = open(filename, 'r')
        json_str = f.read()
        obj = jsonpickle.decode(json_str)
        return obj

    @staticmethod
    async def raw(filename):
        """Gets the raw server data for debugging purposes"""
        filename+=".json"
        f = open(filename, 'r')
        json_str = f.read()
        return json_str

    @staticmethod
    async def getChannel(channels, id):
        """Get a specific channel from a list of channels by ID."""
        for channel in channels:
            if channel.id == id:
                return channel

    @staticmethod
    async def getChannelFromGuild(guilds, server):
        """Get the channel the bot is supposed to talk in from every Discord server connected to."""
        for guild in guilds:
            if str(guild.id) == server.id:
                return await GlobalFunc.getChannel(guild.channels, server.channelID)

    @staticmethod
    async def getRandomDialogue(type):
        """Returns a random dialogue option based on the given type of dialogue."""
        dialogue = await GlobalFunc.read("dialogue")
        r = random.randint(0, len(dialogue[type])-1)
        return dialogue[type][str(r)]

    @staticmethod
    async def calculateETA(end_time):
        """Calculate how much time there is left till people are off Cooldown. Based on UTC time. Not local."""
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific'))  
        date_time_obj = end_time
        now_pacific = now_pacific.replace(tzinfo=None)
        diff = date_time_obj - now_pacific
        minute = diff.seconds//60%60
        hour = diff.seconds//3600
        eta = f"{hour:02}:{minute:02}"+"\n"
        return eta

    @staticmethod
    async def getDisplayName(guild, mention):
        name = mention.replace("<@", "")
        name = name.replace(">", "")
        member = guild.get_member(int(name))
        return member.display_name