import discord
from discord.ext import commands
import asyncio
import os

TOKEN = 'MTA3MTUyNTA4NjQ4NzY2MjYxMg.GLxWeD.TcRi2-9fcpMR7oOQwezXi8EeHbPxHW72QYff60' # DISCORD API TOKEN HERE
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="-", intents=intents)


@commands.command(name='greet')
async def greet(ctx):
    await ctx.send("HELLO")


async def load():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    await load()
    bot.add_command(greet)


if __name__ == '__main__':
    # discord.opus.load_opus("./libopus.so.0.8.0")
    asyncio.run(main())
    bot.run(TOKEN)
