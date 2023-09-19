import discord
from discord.ext import commands
import asyncio
import os

TOKEN = 'DISCORD_BOT_TOKEN'
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix="!",intents=intents)

@commands.command(name='greet')
async def greet(ctx):
    await ctx.send("HELLO")

async def load(): 
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename.startswith('cogs'):
            cog = bot.get_cog(f"{filename[:-3]}")
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    await load()
    bot.add_command(greet) 


if __name__ == '__main__':
    asyncio.run(main())
    bot.run(TOKEN)