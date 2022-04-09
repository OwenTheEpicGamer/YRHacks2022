from database import get_database
from discord.ext import commands
from discord import Color, Embed
from pymongo import ReturnDocument
from random import randint
from datetime import datetime
import dateparser
import timeago

class Tasks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = get_database()

    @commands.command(name='addtask')
    async def addtask(self, ctx: commands.Context, name: str, deadline: str):
        if len(name) > 100:
            await ctx.send(f'{ctx.author.mention} task name is too long!')
            return
        deadline = dateparser.parse(deadline, settings = {
            'TO_TIMEZONE': 'UTC',
            'PREFER_DATES_FROM': 'future'
        })
        if deadline is None:
            await ctx.send(f'{ctx.author.mention} invalid deadline!')
            return
        res = self.db.tasks.update_one(
            { 'user_id': ctx.author.id, 'name': name },
            { '$set': { 'deadline': deadline } },
            upsert=True
        )
        await ctx.send(f'{ctx.author.mention} task **{name}** {"added" if res.upserted_id else "updated"} successfully!')

    @commands.command(name='done')
    async def done(self, ctx: commands.Context, name: str):
        task = self.db.tasks.find_one_and_delete({ 'user_id': ctx.author.id, 'name': name })
        if task is None:
            await ctx.send(f'{ctx.author.mention} task **{name}** does not exist!')
        else:
            now = datetime.utcnow()
            if task['deadline'] >= now:
                pts = randint(3, 7)
                user = self.db.users.find_one_and_update(
                    { 'user_id': ctx.author.id },
                    { '$inc' : { 'points': pts } },
                    upsert=True,
                    return_document=ReturnDocument.AFTER
                )
                feedback = f'You earned {pts} points (current points: {user["points"]})'
            else:
                feedback = "It was overdue, so you didn't earn any points"
            await ctx.send(f'{ctx.author.mention} task **{name}** completed!\n' + feedback)

    @commands.command(name='tasks')
    async def tasks(self, ctx: commands.Context):
        embed = Embed(title='Your Tasks', color=Color.green())
        user_tasks = self.db.tasks.find({ 'user_id': ctx.author.id }).sort('deadline')
        now = datetime.utcnow()
        for x in user_tasks:
            embed.add_field(name=x['name'], value='due ' + timeago.format(x['deadline'], now), inline=False)
        if user_tasks.retrieved == 0:
            await ctx.send(f'{ctx.author.mention} tasks all done!')
        else:
            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Tasks(bot))
