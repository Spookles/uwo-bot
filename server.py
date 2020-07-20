import discord
from discord.ext import tasks, commands

class Server(object):
    def __init__(self, id, channel, list):
        self.id = id
        self.channelID = channel
        self.list = list
        self.fishcounter = 0