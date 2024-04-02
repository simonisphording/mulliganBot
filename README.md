This is a simple bot that posts an opening hand for a deck of choice once per day in a newly created discord thread, followed by a poll to choose a deck for the next day.

## Setup

Install the required packages:
- pillow
- discord.py
- requests

Create a file named conf.py in the utils directory for some basic configurations:

```
token = "YOUR_TOKEN_HERE" # The discord bot token
poll_wait_time = 3600 * 3 # Time before poll closes

default_decklist = "DEFAULT DECKLIST HERE" # a link to the archetype when /randomhand is called without a link to a decklist
daily_format = "pauper" # the metagame page on mtggoldfish to use
```

Your bot is ready to be deployed now. Make sure to use /setchannel to set a channel for a daily mulligan thread.

## Usage

The bot automatically creates a thread once per day where a random starting hand is posted. This is followed up with a poll letting users vote between 3 randomly chosen archetypes of your format of choice.

The bot has the following commands:

- /setchannel - lets moderators set the channel in which daily threads are created
- /randomhand DECK_LINK - creates a random opening hand for the provided mtggoldfish deck list
- /randompack CUBE_ID - creates a random 15 card pack given a cubecobra cube ID

## To Do's

- add an option to use shorthand names: for instance, /starthand familiars should give a deck from the familiars page
- remove the default decklist from /randomhand, give an error message instead
- create command tooltips
- save poll results to a file, so they don't get lost when bot resets