import streamlit as st
from core import HashTable, get_rows_of_data

st.set_page_config(
    page_title="HashLearn",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1.5rem !important;
            max-width: 100% !important;
        }
        div[data-testid="stHorizontalBlock"] { gap: 0.8rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

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

METHOD_DESCRIPTIONS = {
    1: """
**Метод цепочек**

Каждый слот хранит список (цепочку) элементов.

**Вставка:**
1. `index = hash(key) % size`
2. Слот пуст → создаём `[элемент]`
3. Слот занят → добавляем в конец списка

**Особенности:**
- Size может быть меньше числа элементов
- Средняя длина цепочки ≈ load factor
- Худший поиск = длина самой длинной цепочки
""",
    2: """
**Линейное пробирование**

При коллизии идём к следующему слоту последовательно.

**Вставка:**
1. `index = hash(key) % size`
2. Занят → `(index + 1) % size`
3. Повторяем, пока не найдём свободный

**Жёлтым** подсвечены элементы, попавшие не на свой хэш-индекс (пробированные).

**Особенности:**
- ⚠️ Требует `size > числа элементов`
- Кластеризация: занятые слоты слипаются в блоки
- Среднее число проб резко растёт при load > 0.7
""",
    3: """
**Квадратичное пробирование**

При коллизии смещение растёт по треугольным числам `i·(i+1)/2`.

**Вставка:**
1. `index = hash(key) % size`
2. Смещения: `+1, +3, +6, +10, ...`
3. Пока не найдём свободный слот

**Жёлтым** подсвечены элементы, попавшие не на свой хэш-индекс (пробированные).

**Особенности:**
- ⚠️ Требует `size > числа элементов`
- ⚠️ Полное покрытие слотов гарантировано только при `size = 2^k` (16, 32, ...)
- Меньше кластеризации, чем у линейного
""",
}

st.title('HashLearn — обучающая система по хэш-таблицам')

if 'last_search' not in st.session_state:
    st.session_state['last_search'] = ''

# ─── Сайдбар ────────────────────────────────────────────────────────
with st.sidebar:
    st.header('Панель управления')

    # ── Шаг 1 (было: только [16, 32])
    size = st.slider(
        "Размер хэш-таблицы:",
        min_value=10,
        max_value=32,
        value=16,
        step=1,
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

    # ── Предупреждение о неоптимальном size для квадратичного (не блокирует)
    if choice_append_table == 3 and (size & (size - 1)) != 0:
        st.warning(
            f"⚠️ **size={size}** — не степень двойки.\n\n"
            f"Для квадратичного пробирования полное покрытие всех слотов "
            f"гарантировано только при **size = 2^k** (16, 32, ...). "
            f"При size={size} часть слотов может быть недостижима, "
            f"и таблица «заполнится» раньше времени."
        )

    st.divider()
    st.subheader('Поиск по имени')
    search_name = st.text_input('Имя', value='', label_visibility='collapsed')
    search_clicked = st.button('Найти')

    st.divider()
    st.subheader('Легенда подсветки')

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
    else:
        _legend('#fff176', 'Пробированный элемент')  # ← новое
    _legend('#add8e6', 'Найденный элемент')
    _legend('#f5f5f5', 'Пустой слот', '#999')

if search_clicked:
    st.session_state['last_search'] = search_name.strip()

# ─── Построение таблицы ─────────────────────────────────────────────
h = HashTable(size=size)
items = h.get_data(data_load_choice)

if choice_append_table in (2, 3) and len(items) >= size:
    st.error(
        f"Для открытой адресации нужно size > {len(items)}. "
        f"Сейчас size={size}, элементов={len(items)}. Увеличьте размер."
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

# ─── Три колонки ────────────────────────────────────────────────────
col_hash, col_source, col_info = st.columns([1.1, 1.1, 1], gap="medium")

with col_hash:
    st.subheader('Хэш-таблица')
    st.dataframe(h.get_styled_data(), use_container_width=True, hide_index=True)
    st.text(h.get_appending_statistics())

with col_source:
    st.subheader('Исходные данные')
    st.dataframe(get_rows_of_data(items), use_container_width=True, hide_index=True)

with col_info:
    st.subheader('📊 Распределение')

    with st.container(border=True):
        st.markdown(METHOD_DESCRIPTIONS[choice_append_table])

    stats = h.get_distribution_stats()

    with st.container(border=True):
        st.markdown('**Текущая таблица**')
        st.markdown(
            f"- Слотов: {stats['size']}\n"
            f"- Занято: {stats['occupied']}\n"
            f"- Пусто: {stats['empty']}\n"
            f"- Загрузка: {stats['load']:.0%}\n"
            f"- Коллизий/проб: {stats['collision']}"
        )

    if choice_append_table == 1:
        with st.container(border=True):
            st.markdown('**Цепочки**')
            st.markdown(
                f"- Макс. длина: **{stats['max_chain']}**\n"
                f"- Средняя: **{stats['avg_chain']:.2f}**"
            )
            st.caption(f'Худший поиск: {stats["max_chain"]} сравнений')
    else:
        with st.container(border=True):
            st.markdown('**Кластеры**')
            st.markdown(
                f"- Кластеров: **{stats['clusters_count']}**\n"
                f"- Макс. длина: **{stats['max_cluster']}**\n"
                f"- Средняя: **{stats['avg_cluster']:.2f}**"
            )
            if stats['clusters']:
                st.caption('Длины кластеров:')
                st.text('  '.join(str(c) for c in stats['clusters']))
            st.caption(f'Худший поиск: {stats["max_cluster"]} проб')