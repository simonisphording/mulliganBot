import datetime
import discord
from discord.ext import tasks
from utils.decklistFetcher import fetchLatestDecklist
from utils.randomHand import generateHandImage

token = "YOUR_TOKEN_HERE"
channel_id = "YOUR_CHANNEL_ID_HERE"

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
        await message.channel.send(f'a random opening hand from <{url}>')
        hand = generateHandImage(deck)
        await message.channel.send(file=discord.File("images/hand.jpg"))


client.run(token)