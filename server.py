import discord
from discord.ext import tasks, commands

class Server():
    def __init__(self, id, channel, list):
        self.id = id
        self.channel = channel
        self.list = list