import os


def get_secret(n):
    key = None
    if os.path.exists('secret.key'):
        with open('secret.key', 'rb') as f:
            key = f.read()

    if key and len(key) == n:
        return key

    key = os.urandom(n)
    with open('secret.key', 'wb') as f:
        f.write(key)
    return key
