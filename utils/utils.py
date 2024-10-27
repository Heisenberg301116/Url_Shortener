import random

MAX_LEN = 7
DNS = "http://magic.Link"
print("DNS:", DNS)

def create_short_code():
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    length = random.choice(range(1, MAX_LEN + 1))
    short_code = "".join(random.choice(chars) for _ in range(length))
    return short_code