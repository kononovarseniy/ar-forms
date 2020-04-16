import os


def get_secret(n, key_file):
    key = None
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()

    if key and len(key) == n:
        return key

    key = os.urandom(n)
    with open(key_file, 'wb') as f:
        f.write(key)
    return key
