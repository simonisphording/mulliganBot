import urllib


def fetchDecklistID():
    # read mtggoldfish web page
    data = urllib.request.urlopen("https://www.mtggoldfish.com/archetype/pauper-familiars#paper").read()
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