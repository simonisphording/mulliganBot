import os
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
            _, path = generateHandImage(deck)
            await message.channel.send(f'a random opening hand from <{url}>')
            await message.channel.send(file=discord.File(path))
            os.remove(path)
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

    if message.content.startswith('/mulligan'):
        async for msg in message.channel.history(limit=None):
            if msg.author == client.user:
                if msg.content.startswith("a random opening hand from"):
                    url = msg.content.replace("<", ">").split(">")[1]
                    deck, url = fetchLatestDecklist(url)
                    _, path = generateHandImage(deck)
                    await message.channel.send(file=discord.File(path))
                    os.remove(path)
                    break


@tasks.loop(time=dailyTime)
async def dailyHands():
    global next_link
    for guild in client.guilds:
        channel = client.get_channel(get_channel_id(guild.id))
        if not channel:
            print(f"{guild.name} has no channel id")
            break
        if guild.id in next_link.keys():
            deck, url = fetchLatestDecklist(next_link[guild.id])
        else:
            deck, url = fetchLatestDecklist()
        _, path = generateHandImage(deck)

        thread_title = datetime.datetime.now().strftime("%Y-%m-%d")
        thread = await channel.create_thread(name=thread_title)

        await channel.send(f"Today's daily hand thread: {thread.mention}")

        await thread.send(f'a random opening hand from <{url}>. Would you like to see another hand? Type /mulligan')
        await thread.send(file=discord.File(path))
        os.remove(path)

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

        await asyncio.sleep(poll_wait_time)

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
        next_link[guild.id] = topDecks[winner]

        await thread.send(f"Poll closed! Tomorrow's deck will be {winner}")


@client.event
async def on_ready():
    if not dailyHands.is_running():
        dailyHands.start()
        print("dailyHands task started")

client.run(token)