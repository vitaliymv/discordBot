import asyncio

from discord import FFmpegPCMAudio
from discord.ext import commands
import pymysql.cursors
import json
from discord.utils import get
from asyncio import sleep
from youtube_dl import YoutubeDL

client_commands = commands.Bot(command_prefix='!')


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

ydl_opts = {'format': 'bestaudio'}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


@client_commands.command()
async def hello(ctx):
    await ctx.send("Hello i am discord bot")


song_queue = []


def play_next(ctx, arg):
    if len(song_queue) >= 1:
        song_queue.pop(0)
        voice = get(client_commands.voice_clients, guild=ctx.guild)
        voice.play(FFmpegPCMAudio(arg, **FFMPEG_OPTIONS),
                   after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, arg), client_commands.loop))


@client_commands.command()
async def play(ctx, arg):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client_commands.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send("Bot is connected to channel")

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(arg, download=False)
        music_url = info['formats'][0]['url']
        song_queue.append(music_url)
        print(song_queue)
        # voice.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))
        voice.play(FFmpegPCMAudio(music_url, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx, arg))

        while voice.is_playing():
            await sleep(1)
        if not voice.is_paused():
            await voice.disconnect()


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
