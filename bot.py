from config import token
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

bot.load_extension('somecommands')
bot.load_extension('googlecalendar')

@bot.event
async def on_ready():
    print("Bot is ready")

bot.load_extension("somecommands")

bot.run(token)
