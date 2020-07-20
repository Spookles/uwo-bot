import discord
from discord.ext import tasks, commands
import jsonpickle
import random

class GlobalFunc():
    """Functions that get used by multiple cogs."""

    @staticmethod
    async def write(obj, filename):
        filename+=".json"
        f = open(filename, 'w')
        json_obj = jsonpickle.encode(obj)
        f.write(json_obj)
        f.close()

    @staticmethod
    async def read(filename):
        filename+=".json"
        f = open(filename, 'r')
        json_str = f.read()
        obj = jsonpickle.decode(json_str)
        return obj

    @staticmethod
    async def getChannel(channels, id):
        for channel in channels:
            if channel.id == id:
                return channel

    @staticmethod
    async def getChannelFromGuild(guilds, server):
        for guild in guilds:
            if str(guild.id) == server.id:
                return await GlobalFunc.getChannel(guild.channels, server.channelID)

    @staticmethod
    async def getRandomDialogue(type):
        dialogue = await GlobalFunc.read("dialogue")
        r = random.randint(0, len(dialogue[type])-1)
        return dialogue[type][str(r)]