import asyncio
from discord.ext import commands

class Timer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    time = 0
    @commands.command(name='timercreate')
    async def timercreate(self, ctx: commands.Context, timeInput):
        global time
        time = 0
        if timeInput[-1] == 's':
            time - int(timeInput[:-1])
        if timeInput[-1] == 'm':
            time = int(timeInput[:-1]) * 60
        if timeInput[-1] == 'h':
            time = int(timeInput[:-1]) * 3600

        await ctx.send(f'Time is set to {time}')
        
        
        if time > 86400:
            await ctx.send("Timer is too long")
            return
        if time <= 0:
            await ctx.send("Timer is too short")
            return

    @commands.command(name='timerstart')
    async def timerrun(self, ctx: commands.Context):
        global time
        if time >= 3600:
            message = await ctx.send(f"Timer: {time//3600} hours {time%3600//60} minutes {time%60} seconds")
        elif time >= 60:
            message = await ctx.send(f"Timer: {time//60} minutes {time%60} seconds")
        elif time < 60:
            message = await ctx.send(f"Timer: {time} seconds")

        while True:
            try:
                await asyncio.sleep(1)
                time -= 1
                if time <= 0:
                    await message.edit(content="Ended!")
                    await ctx.send(f"{ctx.author.mention} Your countdown Has ended!")
                    break
            except:
                break

    @commands.command(name='time')
    async def time(self, ctx: commands.Context):
        global time
        if time >= 3600:
            await ctx.send(f"Timer: {time//3600} hours {time %3600//60} minutes {time%60} seconds")
        elif time >= 60:
            await ctx.send(f"Timer: {time//60} minutes {time%60} seconds")
        elif time < 60:
            await ctx.send(f"Timer: {time} seconds")        

    @commands.command(name='timerend')
    async def timerend(self, ctx: commands.Context):
        global time
        time = 0

    pomoTime = 0
    count = 0
    isStudy = True

    @commands.command(name='pomodoro')
    
    async def pomodoro(self, ctx: commands.Context, number):  
        await ctx.send(f"{ctx.author.mention} RUN")
        global pomoTime
        global count
        global isStudy

        number = int(number)
        while count <= number:
            await ctx.send(f"{ctx.author.mention} Study session number {count} has started!")
            pomoTime = 1500
            
            isStudy = True
            while True:
                try:
                    await asyncio.sleep(1)
                    pomoTime -= 1
                    if pomoTime <= 0:
                        await ctx.send(f"{ctx.author.mention} Study session number {count} has ended!")
                        break
                except:
                    break

            await ctx.send(f"{ctx.author.mention} Break session number {count} has started!")
            pomoTime = 300
            isStudy = False
            while True:
                try:
                    await asyncio.sleep(1)
                    time -= 1
                    if time <= 0:
                        await ctx.send(f"{ctx.author.mention} Break number {count} has ended!")
                        break
                except:
                    break
            count = count + 1

    
def setup(bot: commands.Bot):
    bot.add_cog(Timer(bot))
