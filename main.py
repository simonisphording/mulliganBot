import os
import datetime
import argparse
import json
import asyncio
import discord
from discord.ext import commands, tasks
from random import sample
from urllib.error import HTTPError
from collections import deque

from utils.decklistFetcher import fetchLatestDecklist, fetchTopDecks
from utils.randomHand import generateHandImage

intents = discord.Intents.default()
intents.message_content = True

guild_tasks = {}
decklist_cache = {}
CACHE_SIZE = 10

bot = commands.Bot(command_prefix='/', intents=intents, case_insensitive=True)

def get_server_directory(guild_id):
    return f"servers/{guild_id}"

def get_settings_file(guild_id):
    return os.path.join(get_server_directory(guild_id), "settings.json")

def ensure_server_directories(guild_id):
    """Ensure directories and settings file exist."""
    server_dir = get_server_directory(guild_id)
    settings_file = get_settings_file(guild_id)

    os.makedirs(server_dir, exist_ok=True)
    if not os.path.exists(settings_file):
        settings = {"daily_channel" : None,
                    "daily_format" : "pauper",
                    "time" : datetime.time(9, 0).strftime("%H:%M"),
                    "default_list" : "https://www.mtggoldfish.com/archetype/pauper-familiars#paper",
                    "make_poll" : False,
                    "poll_wait_time" : 3600 * 5,
                    "last_poll_result" : None}
        save_settings(settings_file, settings)

def load_settings(settings_file):
    """Load settings from JSON file."""
    with open(settings_file, "r") as f:
        return json.load(f)

def save_settings(settings_file, settings):
    """Save settings to JSON file."""
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)
    with open(settings_file, "w") as f:
        json.dump(settings, f)

def get_cached_decklist(guild_id, deck_id):
    if guild_id in decklist_cache:
        for cached_id, cached_deck in decklist_cache[guild_id]:
            if cached_id == deck_id:
                return cached_deck
    return None

def cache_decklist(guild_id, deck_id, deck):
    if guild_id not in decklist_cache:
        decklist_cache[guild_id] = deque(maxlen=CACHE_SIZE)
    decklist_cache[guild_id].append((deck_id, deck))

async def send_hand_image(channel, deck):
    """Generate and send a random hand image."""
    try:
        _, path = generateHandImage(deck)
        msg = await channel.send(file=discord.File(path))
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        os.remove(path)
    except Exception as e:
        print(f"Error sending hand image: {e}")
        await channel.send("An error occurred while generating the hand image.")

@bot.command(name="randomHand", help="Generate a random opening hand from a decklist")
async def random_hand(ctx, deck_link: str = None):
    settings_file = get_settings_file(ctx.guild.id)
    settings = load_settings(settings_file)
    deck_id = deck_link if deck_link else settings["default_list"]

    cached_deck = get_cached_decklist(ctx.guild.id, deck_id)
    if cached_deck:
        deck, url = cached_deck
    else:
        try:
            deck, url = fetchLatestDecklist(deck_id)
            cache_decklist(ctx.guild.id, deck_id, (deck, url))
        except HTTPError:
            await ctx.send(f"https://www.mtggoldfish.com/deck/{deck_id} is not an existing deck")
            return

    await ctx.send(f'a random opening hand from <{url}>')
    await send_hand_image(ctx.channel, deck)

@bot.command(name="mulligan", help="Mulligan the last posted deck")
async def mulligan(ctx):
    posted = False
    async for msg in ctx.channel.history(limit=50):  # Limit to last 50 messages to optimize
        if msg.author == bot.user and msg.content.startswith("a random opening hand from"):
            url = msg.content.replace("<", ">").split(">")[1]
            cached_deck = get_cached_decklist(ctx.guild.id, url)
            if cached_deck:
                deck, _ = cached_deck
            else:
                deck, url = fetchLatestDecklist(url)
                cache_decklist(ctx.guild.id, url, (deck, url))
            await send_hand_image(ctx.channel, deck)
            posted = True
            break

    if not posted and isinstance(ctx.channel, discord.Thread):
        msg = await ctx.channel.parent.fetch_message(ctx.channel.id)
        if msg.content.startswith("a random opening hand from"):
            url = msg.content.replace("<", ">").split(">")[1]
            cached_deck = get_cached_decklist(ctx.guild.id, url)
            if cached_deck:
                deck, _ = cached_deck
            else:
                deck, url = fetchLatestDecklist(url)
                cache_decklist(ctx.guild.id, url, (deck, url))
            await send_hand_image(ctx.channel, deck)


def create_daily_task(guild):
    settings_file = get_settings_file(guild.id)
    settings = load_settings(settings_file)
    daily_time = settings["time"]
    daily_time = datetime.datetime.strptime(daily_time, "%H:%M").time()

    # Define the loop for the specific guild
    @tasks.loop(time=daily_time)
    async def daily_hands():
        try:
            channel = bot.get_channel(settings['daily_channel'])
            if not channel:
                print(f"{guild.name} has no valid daily channel.")
                return

            # Fetch the decklist
            deck_id = settings["last_poll_result"] if settings["make_poll"] and settings["last_poll_result"] else \
            settings["default_list"]

            cached_deck = get_cached_decklist(guild.id, deck_id)
            if cached_deck:
                deck, url = cached_deck
            else:
                deck, url = fetchLatestDecklist(deck_id)
                cache_decklist(guild.id, deck_id, (deck, url))

            # Create a thread for discussion
            thread_title = datetime.datetime.now().strftime("%Y-%m-%d")
            message = await channel.send(
                f'a random opening hand from <{url}>. If you want to see another hand, type /mulligan.')
            thread = await channel.create_thread(name=thread_title, message=message)
            await send_hand_image(thread, deck)

            # Create a poll if needed
            if settings["make_poll"]:
                topDecks = fetchTopDecks(settings["daily_format"])
                rselection = sample(list(topDecks.keys()), 3)
                rselection = dict(zip([chr(0x1F1E6), chr(0x1F1E7), chr(0x1F1E8)], rselection))

                embed = discord.Embed(title="Which archetype would you like to see tomorrow? Poll closes in 3 hours",
                                      color=discord.Color.blue())
                for emoji, option in rselection.items():
                    embed.add_field(name=f"{emoji}: {option}", value="\u200B", inline=False)

                msg = await thread.send(embed=embed)
                for emoji in rselection.keys():
                    await msg.add_reaction(emoji)

                await asyncio.sleep(settings["poll_wait_time"])

                msg = await thread.fetch_message(msg.id)
                max_count = 0
                max_option = []
                for reaction in msg.reactions:
                    emoji = reaction.emoji
                    if emoji in rselection:
                        count = reaction.count - 1
                        if count > max_count:
                            max_count = count
                            max_option = [emoji]
                        elif count == max_count:
                            max_option.append(emoji)

                winner = rselection[sample(max_option, 1)[0]]
                settings["last_poll_result"] = winner
                save_settings(settings_file, settings)
                await thread.send(f"Poll closed! Tomorrow's deck will be {winner}")
        except Exception as e:
            print(f"Error in daily task for {guild.name}: {e}")

    # Start the task and store it
    daily_hands.start()
    guild_tasks[guild.id] = daily_hands

@bot.command(name="setChannel", help="Set channel in which daily hands are posted")
async def set_channel(message, channel: discord.TextChannel = None):
    guild_id = message.guild.id

    if not message.author.guild_permissions.administrator:
        await message.channel.send("You need to be an administrator to set the channel.")
        return

    if not channel:
        await message.channel.send("Please mention a valid channel.")
        return

    settings_file = get_settings_file(guild_id)
    settings = load_settings(settings_file)
    settings["daily_channel"] = channel.id
    save_settings(settings_file, settings)
    await message.channel.send(f"Channel {channel.mention} set as message destination.")

@bot.command(name="setFormat", help="Set format to pull decks from")
async def set_format(message, daily_format: str = None):
    guild_id = message.guild.id

    if not message.author.guild_permissions.administrator:
        await message.channel.send("You need to be an administrator to change settings.")
        return

    if not daily_format:
        await message.channel.send("Please mention a format.")
        return

    settings_file = get_settings_file(guild_id)
    settings = load_settings(settings_file)
    settings["daily_format"] = daily_format
    save_settings(settings_file, settings)
    await message.channel.send(f"{daily_format} set as format.")

@bot.command(name="setDailyTime", help="Set a new UTC time for dailyHands task (HH:MM format)")
async def set_daily_time(ctx, time_str: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.channel.send("You need to be an administrator to set the daily hand time.")
        return

    try:
        # Parse the new time
        new_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        guild_id = ctx.guild.id

        # Load settings
        settings_file = get_settings_file(guild_id)
        settings = load_settings(settings_file)
        settings["time"] = new_time.strftime("%H:%M")
        save_settings(settings_file, settings)

        # Stop and restart the task for this guild
        if guild_id in guild_tasks and guild_tasks[guild_id].is_running():
            guild_tasks[guild_id].stop()
            print(f"Stopped daily task for guild {ctx.guild.name}")

        create_daily_task(ctx.guild)
        await ctx.send(f"Daily task time updated to {time_str}!")

    except ValueError:
        await ctx.send("Invalid time format. Please use HH:MM format.")

@bot.command(name="setDefaultDeck", help="Set default decklist. Can also be an archetype page (i.e. https://www.mtggoldfish.com/archetype/pauper-familiars#paper")
async def set_default_deck(ctx, deck : str = None):
    guild_id = ctx.guild.id

    if not ctx.author.guild_permissions.administrator:
        await ctx.channel.send("You need to be an administrator to change settings.")
        return

    if not deck:
        await ctx.channel.send("Please provide a deck link.")
        return

    settings_file = get_settings_file(guild_id)
    settings = load_settings(settings_file)
    settings["default_list"] = deck
    save_settings(settings_file, settings)
    await ctx.channel.send(f"{deck} set as format.")

@bot.command(name="poll", help="toggle daily poll on or off")
async def toggle_poll(ctx, toggle : str):
    guild_id = ctx.guild.id
    settings_file = get_settings_file(guild_id)
    settings = load_settings(settings_file)

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You need to be an administrator to change settings.")
        return

    toggle = toggle.lower()
    if toggle == "on":
        settings["make_poll"] = True
        await ctx.send("Daily polls have been enabled.")
    elif toggle == "off":
        settings["make_poll"] = False
        await ctx.send("Daily polls have been disabled.")
    else:
        await ctx.send("Invalid option. Use '/poll on' to enable or '/poll off' to disable.")
        return

    save_settings(settings_file, settings)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        ensure_server_directories(guild.id)
        if guild.id not in guild_tasks:
            create_daily_task(guild)
            print(f"Started daily task for {guild.name}")
    print("Bot is ready.")

@bot.event
async def on_guild_join(guild):
    ensure_server_directories(guild.id)
    if guild.id not in guild_tasks:
        create_daily_task(guild)
        print(f"Started daily task for {guild.name}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', type=str, help='the bot token', default=None)
    args = parser.parse_args()

    if not args.token:
        token = os.getenv('DISCORD_BOT_TOKEN')
    else:
        token = args.token

    bot.run(token)

if __name__ == "__main__":
    main()