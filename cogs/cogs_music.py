import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from yt_dlp import YoutubeDL

import requests
import isodate
import asyncio
import random

queues = {}
queue_list = {}
vid_id = {}


def yt_data(url):
    api_key = ""  # GOOGLE API TOKEN HERE
    video_id = url.split("v=")[-1].split("&")[0]
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&part=contentDetails&key={api_key}"
    response = requests.get(api_url)
    video_data = response.json()

    title = video_data['items'][0]['snippet']['title']
    duration_ISO = video_data['items'][0]['contentDetails']['duration']

    duration = isodate.parse_duration(duration_ISO)
    if (duration.total_seconds() < 3600): duration = str(duration)[2:]
    return title, duration


def random_list(anime_name):
    with open("anime_song_list/" + anime_name + ".txt", "r") as file:
        lines = file.readlines()
        random_num = random.randint(1, len(lines))
        for i, line in enumerate(lines, start=1):
            if i == random_num:
                del lines
                return line.strip()
        return "no entry found"


# def next_queue(ctx, id):
#     if queues[id] != []:
#         voice = ctx.guild.voice_client
#         source = queues[id].pop(0)
#         [queue_list[id].pop(0)]
#         voice.play(source, after=lambda x=None: next_queue(ctx, ctx.message.guild.id))


def convert_url(url):
    buf = url
    buf2 = buf.split("www.youtube.com/watch?v=")
    if len(buf2) == 2:
        buf3 = buf2[1].split("&t")
        return buf3[0]
    buf2 = buf.split("youtu.be/")

    if len(buf2) == 2:
        buf3 = buf2[1].split("?t")
        return buf3[0]
    else:
        return "invalid"


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.now_playing = None
        self.playing_id = None
        self.is_playing = False

    def next_queue(self, ctx, id):
        if id in queues and queues[id] != []:
            voice = ctx.guild.voice_client
            source = queues[id].pop(0)
            self.now_playing = queue_list[id].pop(0)
            self.bot.dispatch("up_next", ctx)
            voice.play(source, after=lambda x=None: self.next_queue(ctx, ctx.message.guild.id))
        else:
            self.is_playing = False

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if message.author == self.bot.user:
            return
        if message.content == "Sussy Baka":
            await self.sus(ctx)
            return
        # if str(message.author) == "":
        #     await message.channel.send("")

        # haik = ["Haikyu", "Haikyu!", "Haikyu!!", "Haikyu!!!", "Haikyuu", "Haikyuu!", "Haikyuu!!", "Haikyuu!!!"]
        # for s in haik:
        #     if message.content.lower() == s.lower():
        #         await message.channel.send("")

    # Display next song
    @commands.Cog.listener()
    async def on_up_next(self, ctx):
        self.playing_id = vid_id[ctx.message.guild.id].pop(0)
        embed = discord.Embed(title="Up next",
                              description=f"**:musical_note:   NOW PLAYING - {self.now_playing}  :musical_note:**",
                              color=0x0a9efa)
        embed.set_thumbnail(url="https://img.youtube.com/vi/" + self.playing_id + "/0.jpg")
        await ctx.send(embed=embed, delete_after=5.0)

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
        guild_id = ctx.message.guild.id

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        else:
            if guild_id in queues:
                del queues[guild_id]
                del queue_list[guild_id]
                del vid_id[guild_id]
            await ctx.send("Disconnect")
            self.is_playing = False
            await vc.disconnect()

    @commands.command()
    async def steins_gate(self, ctx):
        r = random_list("steins_gate")
        await self.play(ctx, r)

    @commands.command(aliases=['btr'])
    async def bocchi_the_rock(self, ctx):
        r = random_list("bocchi_the_rock")
        await self.play(ctx, r)

    # Big sus
    @commands.command()
    async def sus(self, ctx):
        url = "https://www.youtube.com/watch?v=grd-K33tOSM"
        if ctx.author.voice is None:
            return

        vc = ctx.voice_client
        voice_channel = ctx.author.voice.channel

        if vc is None:
            await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not self.is_playing:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['url']
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            await asyncio.sleep(3)
            voice.stop()

    # PLay a song. If a song is already being played, queue it.
    @commands.command(aliases=['p'])
    async def play(self, ctx, url=''):
        if ctx.author.voice is None:
            await ctx.send("You are not in a Voice Channel!")
            return

        vc = ctx.voice_client
        voice_channel = ctx.author.voice.channel

        if vc is None:
            await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

        # URL checking
        url_id = convert_url(url)
        if url_id == "invalid":
            await ctx.send("Invalid format!")
            print("check play")
            return
        try:
            data = yt_data("https://www.youtube.com/watch?v=" + url_id)
        except IndexError:
            await ctx.send(f"***Fk you {ctx.message.author.mention}*** :middle_finger:")
            return

        title = data[0]
        duration = data[1]

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        voice = get(self.bot.voice_clients, guild=ctx.guild)

        if not self.is_playing:
            self.playing_id = url_id
            self.now_playing = title + " (" + duration + ")"

            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['url']
            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS),
                       after=lambda x=None: self.next_queue(ctx, ctx.message.guild.id))
            self.is_playing = True
            await ctx.send(f"**🎵  NOW PLAYING - {title} ({duration})  🎵**")
        else:
            await self.queue(ctx, url)

    # Queue a song. If no link is provided, show the queue.
    @commands.command(aliases=['q'])
    async def queue(self, ctx, url=""):
        vc = ctx.guild.voice_client

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
            return
        if not self.is_playing:
            await ctx.send("Play a song first!")
            return
        if url == "":
            await self.print_queue(ctx)
            return

        # URL checking
        url_id = convert_url(url)
        if url_id == "invalid":
            await ctx.send("Invalid format!")
            print("check queue")
            return
        try:
            data = yt_data("https://www.youtube.com/watch?v=" + url_id)
        except IndexError:
            await ctx.send(f"**Fk you {ctx.message.author.mention} :middle_finger:**")
            return

        title = data[0]
        duration = data[1]

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}

        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        source = FFmpegPCMAudio(URL, **FFMPEG_OPTIONS)

        guild_id = ctx.message.guild.id
        entry = title + " (" + duration + ")"

        # Add info of the song into list
        if guild_id in queues:
            queues[guild_id].append(source)
            queue_list[guild_id].append(entry)
            vid_id[guild_id].append(url_id)
        else:
            queues[guild_id] = [source]
            queue_list[guild_id] = [entry]
            vid_id[guild_id] = [url_id]

        await ctx.send(f"Added **{title} ({duration})** to queue :notes:")

    # Print the queue as an embed
    @commands.command(aliases=['cq', 'check'])
    async def print_queue(self, ctx):
        vc = ctx.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        guild_id = ctx.message.guild.id

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        elif not self.is_playing:
            await ctx.send("No song is playing!")
        else:
            if guild_id in queue_list and queue_list[guild_id] != []:
                i = 0
                buf = "**"
                for element in queue_list[guild_id]:
                    i += 1
                    buf += f"{i}. {element}\n\n"
                buf += "**"
                embed = discord.Embed(title="Queue", description=buf, color=0xf5c814)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/797400366505263104/1072207868390031360/5C049A60-57A3-41B4-8698-8DE3A42346E0.jpg")
                await ctx.send(embed=embed)

            else:
                await ctx.send("Queue is empty!")

    # Clear the queue
    @commands.command(aliases=['clearqueue', 'clear'])
    async def clear_queue(self, ctx):
        vc = ctx.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        guild_id = ctx.message.guild.id

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        elif not self.is_playing:
            await ctx.send("No song is playing!")
        else:
            if guild_id in queues:
                queues[guild_id] = []
                queue_list[guild_id] = []
                vid_id[guild_id] = []
            await ctx.send(":broom: **The queue is cleared** :broom: ")

    # Remove a song from the queue
    @commands.command(aliases=['rm'])
    async def remove(self, ctx, song_num):
        vc = ctx.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        guild_id = ctx.message.guild.id
        num = int(song_num) - 1
        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        elif not self.is_playing:
            await ctx.send("No song is playing!")
        else:
            queues[guild_id].pop(num)
            name = queue_list[guild_id].pop(num)
            vid_id[guild_id].pop(num)
            await ctx.send(f"**{song_num}. {name}** *is removed from the queue!*")

    # Show the now playing song
    @commands.command(aliases=['np', 'nowplaying'])
    async def now_playing(self, ctx):
        embed = discord.Embed(title="Now playing",
                              description=f"**{self.now_playing}**",
                              color=0xbbcbfc)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/797400366505263104/1072463627774328912/IMG_6410.jpg")
        embed.set_image(url="https://img.youtube.com/vi/" + self.playing_id + "/0.jpg")
        await ctx.send(embed=embed)

    # Skip the current song
    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        vc = ctx.voice_client
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        guild_id = ctx.message.guild.id

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        elif not self.is_playing:
            await ctx.send("No song is playing!")
        else:
            voice.stop()
            if guild_id in queue_list and queue_list[guild_id] != []:
                await ctx.send(f"SKIPPING SONG :track_next:")
            else:
                await ctx.send("ENDING SONG")

    # Pause the current song
    @commands.command()
    async def pause(self, ctx):
        vc = ctx.voice_client

        if vc is None:
            await ctx.send("I am not connected to a voice channel!")
        else:
            vc.pause()
            await ctx.send("Paused ⏸️")

    # Resume the current song
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
