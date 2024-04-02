import os


def store_in_dict(key, value, path):
    ids = dict()
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                k, v = line.strip().split(',')
                ids[k] = v
    ids[str(key)] = value

    with open(path, 'w') as file:
        for k in ids.keys():
            file.write(f"{k},{ids[k]}\n")


def get_dict_value(query, path='channel_ids.txt'):
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                key, value = line.strip().split(',')
                if str(key) == str(query):
                    return value
    return None


def store_channel_id(guild_id, channel_id, path='channel_ids.txt'):
    return store_in_dict(guild_id, channel_id, path)


def get_channel_id(guild_id, path='channel_ids.txt'):
    return int(get_dict_value(guild_id, path))


def store_last_poll(guild_id, result, path='poll_results.txt'):
    return store_in_dict(guild_id, result, path)


def get_last_poll(guild_id, path='poll_results.txt'):
    return get_dict_value(guild_id, path)
