import discord
from discord.ext import tasks, commands

class Server(object):
    def __init__(self, id, channel, list, users):
        self.users = users
        self.id = id
        self.channelID = channel
        self.list = list
        self.fishcounter = 0
        self.levicounter = 0