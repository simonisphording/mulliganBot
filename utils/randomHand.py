import os
from random import sample
from requests import get
from json import loads
from shutil import copyfileobj
from PIL import Image

def drawSeven(deck):
    return sample(deck, 7)


def saveImage(query):
    card = loads(get(f"https://api.scryfall.com/cards/search?q={query}").text)
    if len(card['data']) > 1:
        card = loads(get(f"https://api.scryfall.com/cards/search?q=!{query}").text)
    img_url = card['data'][0]['image_uris']['png']
    with open('images/cards/' + query + ".png", 'wb') as out_file:
        copyfileobj(get(img_url, stream=True).raw, out_file)


def generateHandImage(deck):
    hand = drawSeven(deck)
    for card in hand:
        if card + ".png" not in os.listdir("images/cards"):
            saveImage(card)

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