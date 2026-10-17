def append_chaining(table, value, index, collision):
    if table[index] is None:
        table[index] = [value]
    else:
        table[index].append(value)
        collision += 1
    return collision, index, False


def append_linear_probing(table, value, index, collision):
    start = index
    attempts = 0
    while table[index] is not None:
        index = (index + 1) % len(table)
        collision += 1
        attempts += 1
        if attempts >= len(table):
            raise RuntimeError("Таблица заполнена")
    table[index] = value
    return collision, index, index != start


def append_quadratic_probing(table, value, index, collision):
    start = index
    i = 1
    attempts = 0
    while table[index] is not None:
        index = (start + i * (i + 1) // 2) % len(table)
        i += 1
        collision += 1
        attempts += 1
        if attempts >= len(table):
            raise RuntimeError("Таблица заполнена (size должен быть степенью двойки)")
    table[index] = value
    return collision, index, index != start