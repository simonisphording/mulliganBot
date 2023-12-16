import discord
from discord.ext import tasks
from utils.decklistFetcher import fetchLatestDecklist, fetchCube
from utils.randomHand import generateHandImage, generatePackImage
from utils.conf import token, channel_id
from urllib.error import HTTPError

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/randomhand'):
        if len(message.content.split(" ")) == 2:
            deck_id = message.content.split(" ")[1]
        else:
            deck_id = None
        try:
            deck, url = fetchLatestDecklist(deck_id)
            hand = generateHandImage(deck)
            await message.channel.send(f'a random opening hand from <{url}>')
            await message.channel.send(file=discord.File("images/hand.jpg"))
        except HTTPError:
            await message.channel.send("https://www.mtggoldfish.com/deck/" + deck_id + " is not an existing deck")

    if message.content.startswith('/randompack'):
        if len(message.content.split(" ")) == 2:
            cube_id = message.content.split(" ")[1]
        else:
            await message.channel.send("please provide a cube ID")
        cube, url = fetchCube(cube_id)
        pack = generatePackImage(cube)
        await message.channel.send(f'a random opening hand from <{url}>')
        await message.channel.send(file=discord.File("images/pack.jpg"))


client.run(token)