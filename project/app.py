import streamlit as st
from core import HashTable, get_rows_of_data

DATA_OPTIONS = {
    1: "👤 Пользователи (users.json)",
    2: "📦 Товары (products.json)",
    3: "📚 Книги (books.json)",
}
HASH_OPTIONS = {
    1: "Полиномиальная",
    2: "FNV-1a",
    3: "Дэна Бернстайна (djb2)",
}
COLLISION_OPTIONS = {
    1: "Метод цепочек",
    2: "Линейное пробирование",
    3: "Квадратичное пробирование",
}

st.title('HashLearn — Обучающая система по хэш-таблицам с открытой адресацией')

if 'last_search' not in st.session_state:
    st.session_state['last_search'] = ''

with st.sidebar:
    st.header('Панель управления')

    size = st.select_slider(
        "Размер хэш-таблицы:",
        options=[16, 32],
        value=16,
    )
    data_load_choice = st.selectbox(
        'Файл с данными',
        options=list(DATA_OPTIONS.keys()),
        format_func=lambda x: DATA_OPTIONS[x],
        index=0,
    )
    choice_hash_func = st.selectbox(
        'Хэш-функция',
        options=list(HASH_OPTIONS.keys()),
        format_func=lambda x: HASH_OPTIONS[x],
        index=0,
    )
    choice_append_table = st.selectbox(
        'Метод разрешения коллизий',
        options=list(COLLISION_OPTIONS.keys()),
        format_func=lambda x: COLLISION_OPTIONS[x],
        index=0,
    )

    st.divider()
    st.subheader('Поиск по имени')
    search_name = st.text_input('Имя', value='', label_visibility='collapsed')
    search_clicked = st.button('Найти')

    st.divider()
    st.subheader('Объяснение выделения цветом')

    def _legend(color: str, label: str, text_color: str = '#000') -> None:
        st.markdown(
            f'<div style="display:flex;align-items:center;margin:3px 0;">'
            f'<div style="width:16px;height:16px;background:{color};'
            f'border:1px solid #bbb;border-radius:3px;margin-right:8px;"></div>'
            f'<span style="color:{text_color};">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    _legend('#c8e6c9', 'Одиночный элемент')
    if choice_append_table == 1:
        _legend('#ffcdd2', 'Начало цепочки')
        _legend('#fff9c4', 'Продолжение цепочки')
    _legend('#add8e6', 'Найденный элемент')
    _legend('#f5f5f5', 'Пустой слот', '#999')

if search_clicked:
    st.session_state['last_search'] = search_name.strip()

h = HashTable(size=size)
items = h.get_data(data_load_choice)

if choice_append_table in (2, 3) and len(items) >= size:
    st.error(
        f"Для открытой адресации нужно size > {len(items)}. "
        f"Сейчас size={size}, элементов={len(items)}. Выберите размер 32."
    )
    st.stop()

try:
    h.build(choice_append_table, choice_hash_func, items)
except RuntimeError as e:
    st.error(f"Не удалось построить таблицу: {e}")
    st.stop()

if st.session_state['last_search']:
    result = h.find_in_table(st.session_state['last_search'])
    if 'не найден' in result:
        st.warning(result)
    else:
        st.success(result)

col1, col2 = st.columns(2)
with col1:
    st.header('Хэш-таблица')
    st.dataframe(h.get_styled_data(), width='stretch', hide_index=True)
    st.text(h.get_appending_statistics())
with col2:
    st.header('Исходные данные')
    st.dataframe(get_rows_of_data(items), width='stretch', hide_index=True)