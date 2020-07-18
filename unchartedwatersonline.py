import discord
import asyncio
from discord.ext import tasks, commands

class UnchartedWatersOnline(commands.Cog):
    """Sea of Wonders section of the bot."""
    def __init__(self, bot):
        self.bot = bot