import discord

client = discord.Client()


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

client.run('OTQyNDY4MDk2NzM4ODc3NTQw.Ygk70A.JxWvQRrtT3CHVF5pn6qIBHyQPtI')
