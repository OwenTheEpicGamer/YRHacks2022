from re import S
from database import get_database
from discord.ext import tasks, commands
from discord import Color, Embed
from pymongo import ReturnDocument
from random import randint
from datetime import datetime
import dateparser
import timeago
import asyncio

OVERDUE_TASK_POINT_PENALTY = 10
COMPLETE_TASK_POINT_REWARD_LOW = 3
COMPLETE_TASK_POINT_REWARD_HIGH = 3

class Tasks(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = get_database()
        self.reminders = {}  # kinda scuffed but wtv

    @commands.Cog.listener()
    async def on_ready(self):
        for task in self.db.tasks.find():
            await self.schedule_task(task)

    async def schedule_task(self, task):
        if task['_id'] in self.reminders:
            self.reminders.pop(task['_id']).cancel()

        now = datetime.utcnow()
        if task['deadline'] < now:
            return

        async def remind():
            await asyncio.sleep((task['deadline'] - now).total_seconds())
            user_discord = await self.bot.fetch_user(task['user_id'])
            user_db = self.db.users.find_one_and_update(
                { 'user_id': task['user_id'] },
                { '$inc' : { 'points': -OVERDUE_TASK_POINT_PENALTY } },
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            await user_discord.send(f'Task **{task["name"]}** is overdue!!!\n'
                + f'As a penalty, you lost {OVERDUE_TASK_POINT_PENALTY} points '
                + f'(current points: {user_db["points"]})\n'
                + 'Everyone in the server has been notified of this (you should be ashamed)')

            shaming_list = []
            for guild in self.bot.guilds:
                for member in guild.members:
                    if member != user_discord:
                        shaming_list.append(member.send(
                            f'A user {user_discord.mention} did not finish their task **{task["name"]} before the deadline!!!\n'
                            + f'As a penalty, they lost {OVERDUE_TASK_POINT_PENALTY} points'))
            await asyncio.gather(*shaming_list)

        self.reminders[task['_id']] = asyncio.create_task(remind())

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
        task = self.db.tasks.find_one_and_update(
            { 'user_id': ctx.author.id, 'name': name },
            { '$set': { 'deadline': deadline } },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        upserted = task['_id'] not in self.reminders
        await self.schedule_task(task)
        await ctx.send(f'{ctx.author.mention} task **{name}** {"added" if upserted else "updated"} successfully!')

    @commands.command(name='done')
    async def done(self, ctx: commands.Context, name: str):
        task = self.db.tasks.find_one_and_delete({ 'user_id': ctx.author.id, 'name': name })
        if task is None:
            await ctx.send(f'{ctx.author.mention} task **{name}** does not exist!')
        else:
            if task['_id'] in self.reminders:
                self.reminders.pop(task['_id']).cancel()
            now = datetime.utcnow()
            if task['deadline'] >= now:
                pts = randint(COMPLETE_TASK_POINT_REWARD_LOW, COMPLETE_TASK_POINT_REWARD_HIGH)
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
        for task in user_tasks:
            embed.add_field(name=task['name'], value='due ' + timeago.format(task['deadline'], now), inline=False)
        if user_tasks.retrieved == 0:
            await ctx.send(f'{ctx.author.mention} tasks all done!')
        else:
            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Tasks(bot))
