import discord
import pymysql.cursors
import json


client = discord.Client()


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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print(client.user.id)
    print(client.user.name)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("get"):
        print(message.author.id)
        print(message.author.name)

        user = await client.fetch_user(message.author.id)
        await user.send("hello")


client.run(DISCORD_TOKEN)


