import streamlit as st
from core import HashTable

st.header('HashLearn - Обучающая система по хэш-таблицам с открытой адресацией')

# choice_append_table = 1 (chaining), choice_hash_func = 3 (Dan Bernstein)
h = HashTable(size=16)
h.build(1, 3, h.get_data(1))

st.dataframe(h.get_styled_data(), use_container_width=True, hide_index=True)
st.text(h.get_appending_statistics())