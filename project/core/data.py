import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / 'data'

FILES = {
    1: DATA_DIR / 'users.json',
    2: DATA_DIR / 'products.json',
    3: DATA_DIR / 'books.json',
}

KEY_LENGTH = 9
PAD_CHAR = 'А'


def make_key(name: str) -> str:
    """Строит ключ из имени: первые 9 символов, добитые до 9 кириллической 'А'."""
    return name.strip()[:KEY_LENGTH].ljust(KEY_LENGTH, PAD_CHAR)


def get_json_file(choice_get_data: int) -> list[dict]:
    """Загружает данные из JSON-файла по номеру набора."""
    if choice_get_data not in FILES:
        raise ValueError(f"Неизвестный набор данных: {choice_get_data}")

    with open(FILES[choice_get_data], 'r', encoding='utf-8') as file:
        return json.load(file)


def append_key_in_json_file(data: list[dict]) -> list[dict]:
    """Возвращает НОВЫЙ список с добавленным полем 'key'.

    Не мутирует вход — если позже добавите кеш, старая версия
    (мутация на месте) могла бы давать сюрпризы.
    """
    return [{**slot, 'key': make_key(slot['name'])} for slot in data]


def get_key_of_slot(name: str) -> str:
    """Возвращает ключ, соответствующий имени (для поиска)."""
    return make_key(name)


def get_rows_of_data(data: list[dict]) -> list[dict]:
    """Возвращает данные в виде списка строк, определяя вторую колонку автоматически."""
    if not data:
        return []

    extra_key = 'value'
    for k in data[0]:
        if k not in ('name', 'key'):
            extra_key = k
            break

    return [
        {'name': item.get('name', ''), extra_key: item.get(extra_key, '')}
        for item in data
    ]