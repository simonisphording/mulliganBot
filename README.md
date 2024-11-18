This is a simple bot that posts an opening hand for a deck of choice once per day in a newly created discord thread, followed by a poll to choose a deck for the next day.

## Setup

Install the required packages:
- pillow
- discord.py
- requests

Use python main.py --help to see all the required input

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