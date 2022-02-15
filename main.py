import asyncio

import discord
from discord.ext import commands
import pymysql.cursors
import json
from discord.utils import get
from asyncio import sleep
from youtube_dl import YoutubeDL


client_commands = commands.Bot(command_prefix='!')


# client = discord.Client()
def getConnection():
    connection = pymysql.connect(host='eu-cdbr-west-02.cleardb.net',
                                 user='ba7528f2bb07ee',
                                 password='f66383ea',
                                 db='heroku_37f7ea8f4ada09e',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


print("connect successful!!")


def global_paths():
    global DISCORD_TOKEN


try:
    with getConnection().cursor() as cursor:
        sql = "select * from system_settings where item = 'common' limit 1;"
        cursor.execute(sql)
        result = cursor.fetchone()
        value = result.get('value')
        settings = json.loads(value)
        DISCORD_TOKEN = settings['discord_token']
finally:
    getConnection().close()


@client_commands.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client_commands))
    print(client_commands.user.id)
    print(client_commands.user.name)


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#
#     if message.content.startswith("get"):
#         print(message.author.id)
#         print(message.author.name)
#
#         user = await client.fetch_user(message.author.id)
#         await user.send("hello")

ytdl_format_options = {'format': 'bestaudio'}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


@client_commands.command()
async def hello(ctx):
    await ctx.send("Hello i am discord bot")


ytdl = YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="joins a voice channel")
    async def join(self, ctx):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            return await ctx.send('You need to be in a voice channel to use this command!')

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            vc = await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
            vc = ctx.voice_client

    @commands.command(description="streams music")
    async def play(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command(description="stops and disconnects the bot from voice")
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def setup(bot):
    bot.add_cog(Music(bot))


@client_commands.command()
async def leave(ctx):
    print("Work")
    channel = ctx.message.author.voice.channel
    voice = get(client_commands.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("Bot leave ", channel)


client_commands.run(DISCORD_TOKEN)
