import pandas as pd

from .data import append_key_in_json_file, get_json_file, get_key_of_slot
from .hash_function import hash_dan_bernstein, hash_fnv1a, hash_polynomial
from .strategies import (
    append_chaining,
    append_linear_probing,
    append_quadratic_probing,
)


class HashTable:

    def __init__(self, size: int):
        self.size = size
        self.slots = [None] * self.size
        self.collision = 0
        self.choice_append_table = None
        self.choice_hash_func = None
        self.extra_key = 'value'
        self.searched = None
        self.probed_slots: set[int] = set()  # ← новое

    def get_data(self, data_load_choice: int) -> list[dict]:
        return append_key_in_json_file(get_json_file(data_load_choice))

    def hash_func_select(self, choice_hash_func: int, key: str) -> int:
        if choice_hash_func == 1:
            return hash_polynomial(key, self.size)
        if choice_hash_func == 2:
            return hash_fnv1a(key, self.size)
        if choice_hash_func == 3:
            return hash_dan_bernstein(key, self.size)
        raise ValueError('Неизвестный номер хеш-функции')

    def append_hash_table(self, item: dict) -> None:
        key = item['key']
        index = self.hash_func_select(self.choice_hash_func, key)

        if self.choice_append_table == 1:
            self.collision, _, _ = append_chaining(
                self.slots, item, index, self.collision
            )
        elif self.choice_append_table == 2:
            self.collision, final, was_probed = append_linear_probing(
                self.slots, item, index, self.collision
            )
            if was_probed:
                self.probed_slots.add(final)
        elif self.choice_append_table == 3:
            self.collision, final, was_probed = append_quadratic_probing(
                self.slots, item, index, self.collision
            )
            if was_probed:
                self.probed_slots.add(final)
        else:
            raise ValueError("Неизвестный метод разрешения коллизий")

    def build(self, choice_append_table: int, choice_hash_func: int, items: list[dict]) -> None:
        self.slots = [None] * self.size
        self.collision = 0
        self.choice_append_table = choice_append_table
        self.choice_hash_func = choice_hash_func
        self.searched = None
        self.extra_key = 'value'
        self.probed_slots = set()  # ← сброс

        if items:
            for k in items[0]:
                if k not in ('name', 'key'):
                    self.extra_key = k
                    break

        if choice_append_table in (2, 3) and len(items) >= self.size:
            raise RuntimeError(
                f"Для открытой адресации нужно size > {len(items)}, "
                f"а у вас size={self.size}. Увеличьте размер таблицы."
            )

        for item in items:
            self.append_hash_table(item)

    def count_occupied(self) -> int:
        return sum(1 for slot in self.slots if slot is not None)

    def get_rows_of_hash_table(self) -> list[dict]:
        rows = []

        for i, slot in enumerate(self.slots):
            if slot is None:
                rows.append({
                    'slot': i + 1,
                    'name': '',
                    self.extra_key: '',
                    '_role': 'empty',
                })
                continue

            if self.choice_append_table == 1:
                chain_length = len(slot)
                for j, item in enumerate(slot):
                    if self.searched == (i, j):
                        role = 'searched'
                    elif chain_length == 1:
                        role = 'single'
                    elif j == 0:
                        role = 'start'
                    else:
                        role = 'continue'

                    rows.append({
                        'slot': i + 1 if j == 0 else '',
                        'name': item.get('name', ''),
                        self.extra_key: item.get(self.extra_key, ''),
                        '_role': role,
                    })
            else:
                # Приоритет: searched > probed > single
                if self.searched == (i, -1):
                    role = 'searched'
                elif i in self.probed_slots:
                    role = 'probed'
                else:
                    role = 'single'

                rows.append({
                    'slot': i + 1,
                    'name': slot.get('name', ''),
                    self.extra_key: slot.get(self.extra_key, ''),
                    '_role': role,
                })

        return rows

    def get_styled_data(self):
        rows = self.get_rows_of_hash_table()
        df = pd.DataFrame(rows, columns=['slot', 'name', self.extra_key, '_role'])
        roles = df['_role']
        df = df.drop(columns=['_role'])

        def highlight(row):
            role = roles[row.name]
            if role == "searched":
                return ['background-color: #add8e6'] * len(row)
            if role == "probed":                          # ← новое
                return ['background-color: #fff176'] * len(row)
            if role == "single":
                return ['background-color: #c8e6c9'] * len(row)
            if role == "start":
                return ['background-color: #ffcdd2'] * len(row)
            if role == "continue":
                return ['background-color: #fff9c4'] * len(row)
            if role == "empty":
                return ['background-color: #f5f5f5; color: #999'] * len(row)
            return [''] * len(row)

        return df.style.apply(highlight, axis=1)

    def get_appending_statistics(self) -> str:
        info = 'Коллизии' if self.choice_append_table == 1 else 'Пробирований'
        occupied = self.count_occupied()
        load = round(occupied / self.size, 2)

        return (
            f"{info}: {self.collision}\n"
            f"Занято: {occupied}\n"
            f"Заполнено: {round(load * 100)}%\n"
        )

    def find_in_table(self, name: str) -> str:
        self.searched = None
        key = get_key_of_slot(name)
        name_norm = name.strip()
        start = self.hash_func_select(self.choice_hash_func, key)

        def matches(item: dict) -> bool:
            return item['key'] == key and item['name'].strip() == name_norm

        if self.choice_append_table == 1:
            slot = self.slots[start]
            if slot is None:
                return f"Элемент с именем '{name}' не найден"
            for j, item in enumerate(slot):
                if matches(item):
                    self.searched = (start, j)
                    return f"Элемент с именем '{item['name']}' найден"
            return f"Элемент с именем '{name}' не найден"

        if self.choice_append_table == 2:
            index = start
            for _ in range(self.size):
                if self.slots[index] is None:
                    return f"Элемент с именем '{name}' не найден"
                if matches(self.slots[index]):
                    self.searched = (index, -1)
                    return f"Элемент с именем '{self.slots[index]['name']}' найден"
                index = (index + 1) % self.size
            return f"Элемент с именем '{name}' не найден"

        if self.choice_append_table == 3:
            if self.slots[start] is not None and matches(self.slots[start]):
                self.searched = (start, -1)
                return f"Элемент с именем '{self.slots[start]['name']}' найден"

            i = 1
            for _ in range(self.size):
                index = (start + i * (i + 1) // 2) % self.size
                if self.slots[index] is None:
                    return f"Элемент с именем '{name}' не найден"
                if matches(self.slots[index]):
                    self.searched = (index, -1)
                    return f"Элемент с именем '{self.slots[index]['name']}' найден"
                i += 1
            return f"Элемент с именем '{name}' не найден"

        raise ValueError("Неизвестный метод разрешения коллизий")

    # ─── Для правой панели ──────────────────────────────────────────

    def _get_clusters(self) -> list[int]:
        n = self.size
        occupied = [slot is not None for slot in self.slots]
        if all(occupied):
            return [n]
        if not any(occupied):
            return []
        start = occupied.index(False)
        clusters: list[int] = []
        current = 0
        for k in range(n):
            i = (start + k) % n
            if occupied[i]:
                current += 1
            else:
                if current > 0:
                    clusters.append(current)
                current = 0
        if current > 0:
            clusters.append(current)
        return clusters

    def _get_chain_distribution(self) -> tuple[dict[int, int], list[int]]:
        chains = [len(slot) for slot in self.slots if slot is not None]
        distribution: dict[int, int] = {}
        for length in chains:
            distribution[length] = distribution.get(length, 0) + 1
        return dict(sorted(distribution.items())), chains

    def get_distribution_stats(self) -> dict:
        if self.choice_append_table is None:
            return {}
        occupied = self.count_occupied()
        stats: dict = {
            'method': self.choice_append_table,
            'size': self.size,
            'occupied': occupied,
            'empty': self.size - occupied,
            'load': occupied / self.size if self.size else 0.0,
            'collision': self.collision,
        }
        if self.choice_append_table == 1:
            distribution, chains = self._get_chain_distribution()
            stats.update({
                'chains_count': len(chains),
                'chain_distribution': distribution,
                'max_chain': max(chains) if chains else 0,
                'avg_chain': sum(chains) / len(chains) if chains else 0.0,
            })
        else:
            clusters = self._get_clusters()
            stats.update({
                'clusters': clusters,
                'clusters_count': len(clusters),
                'max_cluster': max(clusters) if clusters else 0,
                'avg_cluster': sum(clusters) / len(clusters) if clusters else 0.0,
            })
        return stats