from config import token
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

bot.load_extension('somecommands')
bot.load_extension('googlecalendar')
bot.load_extension('antiprocrastination')
bot.load_extension('points')
bot.load_extension('tasks')
bot.load_extension('timer')

@bot.event
async def on_ready():
    print("Bot is ready")

bot.run(token)
