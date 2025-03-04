import requests
import string


def fetchDecklistID(url):
    """Fetches the decklist ID from an MTGGoldfish URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.text

        start = data.find('class="dropdown-item" href="/deck/download/') + len(
            'class="dropdown-item" href="/deck/download/'
        )
        end = data.find('">Text File', start)

        if start == -1 or end == -1:
            raise ValueError("Could not find decklist ID in the webpage.")

        return data[start:end].split('"')[0]  # Extract decklist ID properly

    except requests.exceptions.RequestException as e:
        print(f"Error fetching decklist ID: {e}")
        return None


def fetchLatestDecklist(decklist_id):
    """Fetches the latest decklist from MTGGoldfish."""
    if "mtggoldfish.com" in decklist_id:
        decklist_id = fetchDecklistID(decklist_id)
        if not decklist_id:
            return None, None  # Return empty values on failure

    url = f"https://www.mtggoldfish.com/deck/download/{decklist_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text

        deck = []
        for line in data.splitlines():
            if not line.strip():
                continue
            parts = line.split(' ', 1)
            if len(parts) != 2:
                continue  # Skip invalid lines
            count, name = parts
            deck.extend([name] * int(count))  # Add multiple copies

        return deck, f"https://www.mtggoldfish.com/deck/{decklist_id}"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching decklist: {e}")
        return None, None


def fetchCube(cube_id=None):
    """Fetches a cube list from CubeCobra."""
    url = f"https://cubecobra.com/cube/download/plaintext/{cube_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text

        deck = [card for card in data.splitlines() if card and not card.startswith("#")]

        return deck, f"https://cubecobra.com/cube/overview/{cube_id}"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching cube: {e}")
        return None, None


def fetchTopDecks(format):
    """Fetches the top decks for a given format from MTGGoldfish."""
    url = f"https://www.mtggoldfish.com/metagame/{format}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text

        decks = {}
        for line in data.splitlines():
            if "href='/archetype" in line:
                parts = line.split("'")
                if len(parts) < 4:
                    continue
                link = parts[3]
                name_parts = link.split("/")[2].split("-")
                name = " ".join([x for x in name_parts if not (is_hexadecimal(x) or x == "pauper")])
                decks[name] = f"https://www.mtggoldfish.com{link}"

        return decks

    except requests.exceptions.RequestException as e:
        print(f"Error fetching top decks: {e}")
        return {}


def is_hexadecimal(s):
    """Checks if a string is hexadecimal."""
    return all(c in string.hexdigits for c in s)
