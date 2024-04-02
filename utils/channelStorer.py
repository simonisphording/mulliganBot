import os


def store_channel_id(guild_id, channel_id, path='channel_ids.txt'):
    ids = dict()
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                guild_id_str, channel_id_str = line.strip().split(',')
                ids[guild_id_str] = channel_id_str
    ids[guild_id] = channel_id

    with open(path, 'w') as file:
        for k in ids.keys():
            file.write(f"{k},{ids[k]}\n")

def get_channel_id(guild_id, path='channel_ids.txt'):
    with open(path, 'r') as file:
        for line in file:
            guild_id_str, channel_id_str = line.strip().split(',')
            if guild_id_str == str(guild_id):
                return int(channel_id_str)
    return None
