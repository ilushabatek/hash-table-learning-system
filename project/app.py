import streamlit as st
from core import HashTable, get_rows_of_data

DATA_OPTIONS = {
    1: "👤 Пользователи (users.json)",
    2: "📦 Товары (products.json)",
    3: "📚 Книги (books.json)"
}
HASH_OPTIONS = {
    1: "Полиномиальная",
    2: "FNV-1a",
    3: "Дэна Бернстайна (djb2)"
}
COLLISION_OPTIONS = {
    1: "Метод цепочек",
    2: "Линейное пробирование",
    3: "Квадратичное пробирование"
}

st.title('HashLearn - Обучающая система по хэш-таблицам с открытой адресацией')
with st.sidebar:
    st.header('Панель управления')
    size = st.slider(
        "Выберите размер хэш-таблицы:",
        min_value=10,
        max_value=30,
        value=16,        # значение по умолчанию
        step=1           # шаг изменения
    )
    data_load_choice = st.selectbox(
        'Выберите файл с данными',
        options=list(DATA_OPTIONS.keys()),
        format_func=lambda x: DATA_OPTIONS[x],
        index=0
        
    )
    choice_hash_func = st.selectbox(
        'Выберите хэш-функцию',
        options=list(HASH_OPTIONS.keys()),
        format_func=lambda x: HASH_OPTIONS[x],
        index=0
    )
    choice_append_table = st.selectbox(
        'Выберите метод разрешения коллизий',
        options=list(COLLISION_OPTIONS.keys()),
        format_func=lambda x: COLLISION_OPTIONS[x],
        index=0
    )
    
h = HashTable(size=size)
h.build(choice_append_table, choice_hash_func, h.get_data(data_load_choice))

col1, col2 = st.columns(2)
with col1:
    st.header('Хэш-таблица')
    st.dataframe(h.get_styled_data(), use_container_width=True, hide_index=True)
    st.text(h.get_appending_statistics())
with col2:
    st.header('Исходные данные')
    st.dataframe(get_rows_of_data(h.get_data(data_load_choice)))


