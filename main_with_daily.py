import datetime
import discord
from discord.ext import tasks
from utils.decklistFetcher import fetchLatestDecklist, fetchCube
from utils.randomHand import generateHandImage, generatePackImage
from utils.conf import token, channel_id

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

utc = datetime.timezone.utc
dailyTime = datetime.time(hour=12, minute=0, tzinfo=utc)


@tasks.loop(time=dailyTime)
async def dailyHands():
    print("sending daily message")
    channel = client.get_channel(channel_id)
    deck, url = fetchLatestDecklist()
    await channel.send(f'3 random opening hands from <{url}>')
    hand = generateHandImage(deck)
    await channel.send(f'hand 1', file=discord.File("images/hand.jpg"))
    hand = generateHandImage(deck)
    await channel.send(f'hand 2', file=discord.File("images/hand.jpg"))
    hand = generateHandImage(deck)
    await channel.send(f'hand 3', file=discord.File("images/hand.jpg"))
    # do your stuff


@client.event
async def on_ready():
    if not dailyHands.is_running():
        dailyHands.start()
        print("dailyHands task started")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/randomhand'):
        if len(message.content.split(" ")) == 2:
            deck_id = message.content.split(" ")[1]
        else:
            deck_id = None
        deck, url = fetchLatestDecklist(deck_id)
        hand = generateHandImage(deck)
        await message.channel.send(f'a random opening hand from <{url}>')
        await message.channel.send(file=discord.File("images/hand.jpg"))

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