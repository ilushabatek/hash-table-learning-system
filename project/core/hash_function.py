def hash_polynomial(key, size):
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) % size
    return h


def hash_Dan_Bernstein(key, size):
    h = 5381
    for ch in key:
        h = ((h << 5) + h + ord(ch)) % size   # h * 33 + ord(ch)
    return h


def hash_FNV1a(key, size):
    FNV_OFFSET = 2166136261
    FNV_PRIME = 16777619

    h = FNV_OFFSET
    for ch in key:
        h ^= ord(ch)
        h = (h * FNV_PRIME) & 0xFFFFFFFF   # оставляем 32 бита
    return h % size