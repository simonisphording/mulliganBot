import urllib
from utils.conf import default_decklist, daily_format
import string


def fetchDecklistID(url=default_decklist):
    # read mtggoldfish web page
    data = urllib.request.urlopen(url).read()
    data = data.decode("utf-8")

    # find the download link for the decklist
    start = data.find('class="dropdown-item" href="/deck/download/') + len(
        'class="dropdown-item" href="/deck/download/')
    end = data.find('">Text File')
    page = data[start:end]
    return page


def fetchLatestDecklist(decklist_id=None):
    if decklist_id is None:
        decklist_id = fetchDecklistID()
    if "mtggoldfish.com" in decklist_id:
        decklist_id = fetchDecklistID(decklist_id)

    data = urllib.request.urlopen("https://www.mtggoldfish.com/deck/download/" + decklist_id).read().decode("utf-8")

    deck = []
    for card in data.split('\r\n'):
        if card == '':
            break
        n = card.split(' ')[0]
        name = ' '.join(card.split(' ')[1:])
        deck += [name] * int(n)

    return deck, "https://www.mtggoldfish.com/deck/" + decklist_id


def fetchCube(cube_id=None):
    data = urllib.request.urlopen("https://cubecobra.com/cube/download/plaintext/" + cube_id).read().decode("utf-8")
    deck = []
    for card in data.split('\r\n'):
        if card == '':
            break
        if card.startswith('#'):
            continue
        deck.append(card)
    return deck, "https://cubecobra.com/cube/overview/" + cube_id


def fetchTopDecks(format=None):
    if format is None:
        format = daily_format
    data = urllib.request.urlopen("https://www.mtggoldfish.com/metagame/" + format).read()
    data = data.decode("utf-8")
    decks = dict()
    for line in data.split("\n"):
        if "href=\'/archetype" in line:
            link = line.split("\'")[3]
            name = link.split("/")[2]
            name = " ".join([x for x in name.split("-") if not (is_hexadecimal(x) or x == "pauper")])
            decks[name] = "https://www.mtggoldfish.com" + link
    return decks


def is_hexadecimal(s):
    return all(c in string.hexdigits for c in s)
