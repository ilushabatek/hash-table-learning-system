import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES = {
    1: BASE_DIR / 'data' / 'users.json',
    2: BASE_DIR / 'data' / 'products.json',
    3: BASE_DIR / 'data' / 'books.json',
}


def make_key(name):
    """Строит ключ из имени: первые 9 символов, добитые до 9 кириллической 'А'."""
    return name.strip()[:9].ljust(9, 'А')


def get_json_file(choice_get_data):
    """Загружает данные из JSON-файла по номеру набора."""
    if choice_get_data not in FILES:
        raise ValueError(f"Неизвестный набор данных: {choice_get_data}")

    with open(FILES[choice_get_data], 'r', encoding='utf-8') as file:
        return json.load(file)


def append_key_in_json_file(data):
    """Добавляет ключ 'key' каждому элементу списка."""
    for slot in data:
        slot['key'] = make_key(slot['name'])
    return data


def get_key_of_slot(name):
    """Возвращает ключ, соответствующий имени (для поиска)."""
    return make_key(name)


def get_rows_of_data(data):
    """Возвращает данные в виде списка строк, автоматически определяя название второй колонки."""
    if not data:
        return []

    # 1. Ищем название второго ключа (пропускаем 'name' и 'key')
    extra_key = 'value'  # запасной вариант
    for k in data[0]:
        if k not in ('name', 'key'):
            extra_key = k
            break

    # 2. Формируем строки ТОЛЬКО из двух колонок
    rows = []
    for item in data:
        rows.append({
            'name': item.get('name', ''),
            extra_key: item.get(extra_key, '') 
        })
        
    return rows
