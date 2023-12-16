import os
import datetime
from random import sample
from requests import get
from json import loads
from shutil import copyfileobj
from PIL import Image

def drawSeven(deck, n=7):
    return sample(deck, n)


def saveImage(query):
    card = loads(get(f"https://api.scryfall.com/cards/search?q={query}").text)
    if len(card['data']) > 1:
        card = loads(get(f"https://api.scryfall.com/cards/search?q=!\"{query}\"").text)
    if "card_faces" in card['data'][0].keys():
        img_url = card['data'][0]['card_faces'][0]['image_uris']['png']
    else:
        img_url = card['data'][0]['image_uris']['png']
    with open('images/cards/' + query + ".png", 'wb') as out_file:
        copyfileobj(get(img_url, stream=True).raw, out_file)


def set_file_last_modified(file_path, dt):
    dt_epoch = dt.timestamp()
    os.utime(file_path, (dt_epoch, dt_epoch))


def removeOld(path="images/cards", maxCards=10):
    files = [x for x in os.listdir(path) if not x.startswith('.')]
    full_path = [path + "/{0}".format(x) for x in files]
    while len(files) > maxCards:
        oldest_file = min(full_path, key=os.path.getctime)
        os.remove(oldest_file)
        print("removed " + oldest_file)
        files = [x for x in os.listdir(path) if not x.startswith('.')]
        full_path = [path + "/{0}".format(x) for x in files]


def generateHandImage(deck):
    hand = drawSeven(deck)

    # check if directory exceeds max number of cards
    removeOld()

    for card in hand:
        if card + ".png" not in os.listdir("images/cards"):
            saveImage(card)
        else:
            now = datetime.datetime.now()
            set_file_last_modified("images/cards/" + card + ".png", now)

    images = [Image.open("images/cards/" + x + ".png") for x in hand]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save('images/hand.jpg')

    return hand


def generatePackImage(cube):
    pack = drawSeven(cube, n=15)
    for card in pack:
        if card + ".png" not in os.listdir("images/cards"):
            saveImage(card)

    images = [Image.open("images/cards/" + x + ".png") for x in pack]

    width, height = images[0].size
    new_im = Image.new('RGB', (width * 5, height * 3))

    x_offset = 0
    y_offset = 0
    i = 0
    for im in images:
        new_im.paste(im, (x_offset, y_offset))
        x_offset += width
        i += 1
        if i % 5 == 0:
            y_offset += height
            x_offset = 0

    new_im.save('images/pack.jpg')

    return pack
