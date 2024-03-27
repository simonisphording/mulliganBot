import discord
import datetime
from discord.ext import tasks, commands
from utils.decklistFetcher import fetchLatestDecklist, fetchCube, fetchTopDecks
from utils.randomHand import generateHandImage, generatePackImage
from utils.conf import token, channel_id
from urllib.error import HTTPError
from random import sample
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

next_link = None

utc = datetime.timezone.utc
dailyTime = datetime.time(hour=12, minute=0, tzinfo=utc)

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
        try:
            cube, url = fetchCube(cube_id)
            pack = generatePackImage(cube)
            await message.channel.send(f'a random opening hand from <{url}>')
            await message.channel.send(file=discord.File("images/pack.jpg"))
        except HTTPError:
            await message.channel.send("https://cubecobra.com/cube/overview/" + cube_id + " is not an existing cube")


@tasks.loop(time=dailyTime)
async def dailyHands():
    global next_link
    channel = client.get_channel(channel_id)
    deck, url = fetchLatestDecklist(next_link)
    hand = generateHandImage(deck)

    thread_title = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    thread = await channel.create_thread(name=thread_title)

    await channel.send(f"Today's daily hand thread: {thread.mention}")

    await thread.send(f'a random opening hand from <{url}>')
    await thread.send(file=discord.File("images/hand.jpg"))

    topDecks = fetchTopDecks()
    rselection = sample(list(topDecks.keys()), 3)

    rselection = dict(zip([chr(0x1F1E6), chr(0x1F1E7), chr(0x1F1E8)], rselection))

    embed = discord.Embed(title="Which archetype would you like to see tomorrow? Poll closes in 3 hours",
                          color=discord.Color.blue())
    for emoji, option in zip(rselection.keys(), rselection.values()):
        embed.add_field(name=f"{emoji}: {option}", value="\u200B", inline=False)

    msg = await thread.send(embed=embed)

    for emoji in rselection.keys():
        await msg.add_reaction(emoji)

    await asyncio.sleep(3600 * 3)  # wait 3 hours

    # retrieve results
    msg = await thread.fetch_message(msg.id)
    max_count = 0
    max_option = []
    for reaction in msg.reactions:
        emoji = reaction.emoji
        if emoji in rselection.keys():
            count = reaction.count - 1
            if count > max_count:
                max_count = count
                max_option = [emoji]
            elif count == max_count:
                max_option.append(emoji)
    winner = rselection[sample(max_option, 1)[0]]
    next_link = topDecks[winner]

    await thread.send(f"Poll closed! Tomorrow's deck will be {winner}")


@client.event
async def on_ready():
    if not dailyHands.is_running():
        dailyHands.start()
        print("dailyHands task started")

client.run(token)