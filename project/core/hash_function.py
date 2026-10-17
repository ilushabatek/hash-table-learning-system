def hash_polynomial(key: str, size: int) -> int:
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) % size
    return h


def hash_fnv1a(key: str, size: int) -> int:
    FNV_OFFSET = 2166136261
    FNV_PRIME = 16777619
    h = FNV_OFFSET
    for ch in key:
        h ^= ord(ch)
        h = (h * FNV_PRIME) & 0xFFFFFFFF
    return h % size


def hash_dan_bernstein(key: str, size: int) -> int:
    h = 5381
    for ch in key:
        h = ((h << 5) + h + ord(ch)) % size
    return h