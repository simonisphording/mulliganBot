This is a simple bot that posts 3 random opening hands from the latest deck featured on the mtggoldfish.com familiars page.

## Setup

Install the required packages:
- pillow
- discord.py
- requests

Make sure to set the bot token and channel id in main.py

## Usage

This bot automatically posts 3 random sample hands at 12:00 UTC. Another sample hand can be requested using `/randomhand`. If you want to generate a sample hand from a different hand, you can include the deck ID like this: `/randomhand 6015401`.

## To Do's
add an option to use shorthand names: for instance, /starthand familiars should give a deck from the familiars page
