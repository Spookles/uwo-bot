# Huggles the Uncharted Waters Online bot

Huggles is a Discord bot for Uncharted Waters Online. The goal of Huggles is to help you with all sorts of tasks that the game doesn't do itself yet!

## Getting Started

### Prerequisites
Some things you need to install in order for Huggles to work

[Python3](https://www.python.org/downloads/)  
[Discordpy](https://pypi.org/project/discord.py/)  
[dotenv](https://pypi.org/project/python-dotenv/)  
[pytz](https://pypi.org/project/pytz/)  

### Setting up .env
In order for Huggles to know to which bot he is supposed to connect you need to give him a bot token.  
[More info here](https://discordpy.readthedocs.io/en/latest/discord.html)

You need to create a `.env` file in the root folder.
Inside the `.env` you have to write the line:
```
DISCORD_TOKEN=   YOUR TOKEN HERE
```

### Limitations for the time being
Your Discord server needs a chatting channel named `general`. As Huggles needs a channel to automatically write in when the cooldowns the for the Sea of Wonder are over.

## How to run
Once the packages are installed and the .env file is added all that is left is giving a life to Huggles!
In your terminal type: `python3 main.py` and you should get greeted by a list of Discord servers your Huggles is connected to!  

To test Huggles type `!how` in a Discord channel.

