import discord
from discord.ext import tasks, commands

class User(object):
    def __init__(self, id):
        self.id = id
        self.runs = 0

    def increment(self):
        self.runs+=1

def addUser(server, id):
    id = removeCharacters(id)
    newUser = User(id)
    server.users[id] = newUser
    return server

def removeCharacters(id):
    return id.translate(str.maketrans({'<': '', '@': '', '!': '', '>': ''}))