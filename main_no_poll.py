import sys
import discord
import datetime
from discord.ext import tasks, commands
from utils.decklistFetcher import fetchLatestDecklist, fetchCube, fetchTopDecks
from utils.randomHand import generateHandImage, generatePackImage
from utils.channelStorer import store_channel_id, get_channel_id
from utils.conf import token, poll_wait_time
from urllib.error import HTTPError
from random import sample
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

next_link = dict()

utc = datetime.timezone.utc
dailyTime = datetime.time(hour=12, minute=0, tzinfo=utc)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/setchannel'):
        if message.author.guild_permissions.administrator:
            channel_mention = message.channel_mentions[0] if message.channel_mentions else None
            if channel_mention:
                store_channel_id(message.guild.id, channel_mention.id)
                await message.channel.send(f"Channel {channel_mention.mention} set as message destination.")
            else:
                await message.channel.send("Please mention a valid channel.")
        else:
            await message.channel.send("You need to be an administrator to set the channel.")

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


@tasks.loop(time=dailyTime)
async def dailyHands():
    global next_link
    for guild in client.guilds:
        channel = client.get_channel(get_channel_id(guild.id))
        if not channel:
            print(f"{guild.name} has no channel id")
            break
        deck, url = fetchLatestDecklist()
        hand = generateHandImage(deck)

        thread_title = datetime.datetime.now().strftime("%Y-%m-%d")
        thread = await channel.create_thread(name=thread_title)

        await channel.send(f"Today's daily hand thread: {thread.mention}")

        await thread.send(f'a random opening hand from <{url}>. If you want to see another hand, type /randomhand.')
        await thread.send(file=discord.File("images/hand.jpg"))


@client.event
async def on_ready():
    if not dailyHands.is_running():
        dailyHands.start()
        print("dailyHands task started")

client.run(token)