import pandas as pd

from .data import append_key_in_json_file, get_json_file, get_key_of_slot
from .hash_function import hash_Dan_Bernstein, hash_FNV1a, hash_polynomial
from .strategies import append_chaining, append_linear_probing, append_quadratic_probing


class HashTable:

    def __init__(self, size):
        self.size = size
        self.slots = [None] * self.size
        self.used = 0
        self.collision = 0
        self.choice_append_table = None
        self.choice_hash_func = None
        self.extra_key = 'value'
        self.searched = None  # <-- 1. ДОБАВИЛИ: здесь будем хранить координаты найденного элемента

    def get_data(self, data_load_choice):
        """Загружает и подготавливает данные из JSON-файла."""
        
        return append_key_in_json_file(get_json_file(data_load_choice))

    def hash_func_select(self, choice_hash_func, key):
        """Выбор хеш-функции."""
        
        if choice_hash_func == 1:
            return hash_polynomial(key, self.size)
        elif choice_hash_func == 2:
            return hash_FNV1a(key, self.size)
        elif choice_hash_func == 3:
            return hash_Dan_Bernstein(key, self.size)
        raise ValueError('Неизвестный номер хеш-функции')

    def append_hash_table(self, item):
        """Добавление одного элемента в таблицу."""
        
        key = item['key']
        index = self.hash_func_select(self.choice_hash_func, key)

        if self.choice_append_table == 1:
            self.collision = append_chaining(self.slots, item, index, self.collision)
        elif self.choice_append_table == 2:
            self.collision = append_linear_probing(self.slots, item, index, self.collision)
        elif self.choice_append_table == 3:
            self.collision = append_quadratic_probing(self.slots, item, index, self.collision)
        else:
            raise ValueError("Неизвестный метод разрешения коллизий")

        self.used += 1

    def build(self, choice_append_table, choice_hash_func, items):
        """Сбрасывает состояние и строит таблицу заново."""
        
        self.slots = [None] * self.size
        self.used = 0
        self.collision = 0
        self.choice_append_table = choice_append_table
        self.choice_hash_func = choice_hash_func
        self.searched = None  # <-- 2. Сбрасываем поиск при пересборке таблицы

        if items:
            for k in items[0]: 
                if k not in ('name', 'key'):
                    self.extra_key = k
                    break

        for item in items:
            self.append_hash_table(item)

    def count_occupied(self):
        """Количество занятых слотов."""
        
        return sum(1 for slot in self.slots if slot is not None)

    def get_rows_of_hash_table(self):
        """Возвращает список строк для отображения таблицы."""
        
        rows = []

        for i, slot in enumerate(self.slots):
            if slot is None:
                rows.append({
                    'slot': i,
                    'name': '',
                    self.extra_key: '',
                    '_role': 'empty',
                })
                continue

            if self.choice_append_table == 1:
                chain_length = len(slot)
                for j, item in enumerate(slot):
                    # <-- 3. ПРОВЕРЯЕМ, НАЙДЕН ЛИ ЭТОТ ЭЛЕМЕНТ
                    if self.searched == (i, j):
                        role = 'searched'
                    elif chain_length == 1:
                        role = 'single'
                    elif j == 0:
                        role = 'start'
                    else:
                        role = 'continue'

                    rows.append({
                        'slot': i if j == 0 else '',
                        'name': item.get('name', ''),
                        self.extra_key: item.get(self.extra_key, ''),
                        '_role': role,
                    })
            else:
                # <-- 3. ПРОВЕРЯЕМ, НАЙДЕН ЛИ ЭТОТ ЭЛЕМЕНТ
                if self.searched == (i, -1):
                    role = 'searched'
                else:
                    role = 'single'

                rows.append({
                    'slot': i,
                    'name': slot.get('name', ''),
                    self.extra_key: slot.get(self.extra_key, ''),
                    '_role': role,
                })

        return rows

    def get_styled_data(self):
        """Возвращает DataFrame со стилями для Streamlit."""
        
        rows = self.get_rows_of_hash_table()
        df = pd.DataFrame(rows, columns=['slot', 'name', self.extra_key, '_role'])

        # 1. Запоминаем роли в отдельную переменную
        roles = df['_role']
        
        # 2. БЕЗЖАЛОСТНО УДАЛЯЕМ колонку _role из самого DataFrame
        df = df.drop(columns=['_role'])

        def highlight(row):
            # 3. Берем роль по индексу строки (row.name - это индекс строки)
            role = roles[row.name]
            
            if role == "searched":
                return ['background-color: #add8e6'] * len(row)  # Светло-голубой
            if role == "single":
                return ['background-color: #c8e6c9'] * len(row)
            if role == "start":
                return ['background-color: #ffcdd2'] * len(row)
            if role == "continue":
                return ['background-color: #fff9c4'] * len(row)
            if role == "empty":
                return ['background-color: #f5f5f5; color: #999'] * len(row)
            return [''] * len(row)

        # 4. Применяем стили к DataFrame, в котором УЖЕ НЕТ колонки _role
        styler = df.style.apply(highlight, axis=1)
        return styler

    def get_appending_statistics(self):
        """Возвращает строку со статистикой таблицы."""
        
        info = 'Коллизии' if self.choice_append_table == 1 else 'Пробирований'
        occupied = self.count_occupied()
        load = round(occupied / self.size, 2)

        return (
            f"{info}: {self.collision}\t\t\t"
            f"Занято слотов: {occupied} из {self.size}\t\t\t"
            f"Коэффициент заполненности: {load}"
        )

    def find_in_table(self, name):
        """Поиск элемента по имени с учётом выбранного метода."""
        
        self.searched = None  # <-- Сбрасываем прошлый поиск перед новым
        key = get_key_of_slot(name)
        start = self.hash_func_select(self.choice_hash_func, key)

        if self.choice_append_table == 1:
            slot = self.slots[start]
            if slot is None:
                return f"Элемент с именем '{name}' не найден"
            for j, item in enumerate(slot):
                if item['key'] == key:
                    self.searched = (start, j)  # <-- Запоминаем координаты
                    return f"Элемент с именем '{item['name']}' найден"
            return f"Элемент с именем '{name}' не найден"

        if self.choice_append_table == 2:
            index = start
            for _ in range(self.size):
                if self.slots[index] is None:
                    return f"Элемент с именем '{name}' не найден"
                if self.slots[index]['key'] == key:
                    self.searched = (index, -1)  # <-- Запоминаем индекс слота
                    return f"Элемент с именем '{self.slots[index]['name']}' найден"
                index = (index + 1) % self.size
            return f"Элемент с именем '{name}' не найден"

        if self.choice_append_table == 3:
            if self.slots[start] is not None and self.slots[start]['key'] == key:
                self.searched = (start, -1)  # <-- Запоминаем индекс слота
                return f"Элемент с именем '{self.slots[start]['name']}' найден"

            i = 1
            for _ in range(self.size):
                index = (start + i * i) % self.size
                if self.slots[index] is None:
                    return f"Элемент с именем '{name}' не найден"
                if self.slots[index]['key'] == key:
                    self.searched = (index, -1)  # <-- Запоминаем индекс слота
                    return f"Элемент с именем '{self.slots[index]['name']}' найден"
                i += 1
            return f"Элемент с именем '{name}' не найден"

        raise ValueError("Неизвестный метод разрешения коллизий")