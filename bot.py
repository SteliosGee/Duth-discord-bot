import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import discord
from discord.ext import commands
import config
import asyncio
from tasks import feed_checker, status_checker

global_bot_commands = []

# Setup intents and bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("-help"))
    print(os.getcwd())
    print("Bot is ready.")
    if config.hostname == "ihubot":
        
        bot.loop.create_task(status_checker.check_duth_status(bot))
    else:
        print("Running locally. Background tasks not started.")
        bot.loop.create_task(feed_checker.check_feed(bot))

async def load_extensions():
    await bot.load_extension('commands.duth')
    await bot.load_extension('commands.kavala')
    await bot.load_extension('commands.info')
    await bot.load_extension('commands.bot_commands')

async def main():
    await load_extensions()
    await bot.start(config.TOKEN)

# Run the bot
asyncio.run(main())