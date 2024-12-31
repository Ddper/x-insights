import hashlib


def hash_url(url: str) -> str:
    return hashlib.shake_256(url.encode()).hexdigest(16)
