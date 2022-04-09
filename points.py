from database import get_database
from discord.ext import commands
from discord import Color, Embed, Member
from pymongo import ReturnDocument
from random import randint

class Points(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = get_database()

    @commands.command(name='gimme')
    async def gimme(self, ctx: commands.Context, pts: int):
        self.db.users.update_one({ 'user_id': ctx.author.id }, { '$inc' : { 'points': pts } }, upsert=True)
        await ctx.send(f'{ctx.author.mention}! awarded {pts} points!')

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx: commands.Context):
        embed = Embed(title='Point Leaderboard', color=Color.blue())
        for user_db in self.db.users.find().sort('points', -1):
            if 'points' in user_db:
                user_discord = await self.bot.fetch_user(user_db['user_id'])
                embed.add_field(name=user_discord.name, value=user_db['points'], inline=False)
        await ctx.send(embed=embed)

    # A little bit of trolling
    @commands.command(name='attack')
    async def fight(self, ctx: commands.Context, target: Member):
        damage = randint(1, 5)
        opponent = self.db.fight.find_one_and_update(
            { 'user_id': target.id },
            { '$inc' : { 'hp': -damage } },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        await ctx.send(f'{ctx.author.mention} attacked {target} for {damage} damage!\nThey are now at {opponent["hp"]} HP')

    @commands.command(name='heal')
    async def heal(self, ctx: commands.Context):
        player = self.db.fight.find_one_and_update(
            { 'user_id': ctx.author.id },
            { '$inc' : { 'hp': 2 } },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        await ctx.send(f'{ctx.author.mention} healed 2 HP!\nThey are now at {player["hp"]} HP!')


def setup(bot: commands.Bot):
    bot.add_cog(Points(bot))
