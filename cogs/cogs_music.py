import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

import requests
import isodate

queues = {}

def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        voice.play(source)


def yt_data(url):
    api_key = ""
    video_id = url.split("v=")[-1].split("&")[0]
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&part=contentDetails&key={api_key}"
    response = requests.get(api_url)
    video_data = response.json()

    title = video_data['items'][0]['snippet']['title']
    duration_ISO = video_data['items'][0]['contentDetails']['duration']

    duration = isodate.parse_duration(duration_ISO)
    if (duration.total_seconds() < 3600): duration = str(duration)[2:]
    return title, duration


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is Online!")

    @commands.command(pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in a Voice Channel!")
            return

        voice_channel = ctx.author.voice.channel
        vc = ctx.voice_client

        if vc is None:
            await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        vc = ctx.voice_client

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        else:
            await vc.disconnect()

    @commands.command(aliases=['p'])
    async def play(self, ctx, url):
        data = yt_data(url)
        title = data[0]
        duration = data[1]

        if ctx.author.voice is None:
            await ctx.send("You are not in a Voice Channel!")
            return

        vc = ctx.voice_client
        voice_channel = ctx.author.voice.channel

        if vc is None:
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            vc = await vc.move_to(voice_channel)

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
            voice.is_playing()
            await ctx.send(f"**🎵  NOW PLAYING - {title} ({duration})  🎵**")
        else:
            await ctx.send("Already playing song")
            return

    @commands.command(aliases=['q'])
    async def queue(self, ctx, url):
        vc = ctx.guild.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        elif not voice.is_playing():
            await ctx.send("Play a song first!")
        else:
            data = yt_data(url)
            title = data[0]
            duration = data[1]

            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}

            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            source = FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)

            guild_id = ctx.message.guild.id

            if guild_id in queues:
                queues[guild_id].append(source)
            else:
                queues[guild_id] = [source]
            await ctx.send(f"Added **{title} ({duration})** to queue")

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        vc = ctx.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        elif not voice.is_playing():
            await ctx.send("No song is playing!")
        else:
            voice.stop()
            await ctx.send("SKIPPING SONG")

    @commands.command()
    async def pause(self, ctx):
        vc = ctx.voice_client

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        else:
            vc.pause()
            await ctx.send("Paused ⏸️")

    @commands.command()
    async def resume(self, ctx):
        vc = ctx.voice_client

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        else:
            vc.resume()
            await ctx.send("Resume ▶️")


async def setup(bot):
    await bot.add_cog(Music(bot))
