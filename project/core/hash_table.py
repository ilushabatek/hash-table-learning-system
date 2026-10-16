import pandas as pd
from hash_function import hash_Dan_Bernstein, hash_FNV1a, hash_polynomial
from strategies import append_chaining, append_linear_probing, append_quadratic_probing

data = [
    {'key': 'ASGDF12', 'name': 'Игорь', 'balance': '912481245'},
    {'key': 'BHTKE45', 'name': 'Анна', 'balance': '534872190'},
    {'key': 'CVLMW78', 'name': 'Дмитрий', 'balance': '781245903'},
    {'key': 'DQXNP01', 'name': 'Елена', 'balance': '245918376'},
    {'key': 'ERZQO34', 'name': 'Сергей', 'balance': '659283471'},
    {'key': 'FSAUR67', 'name': 'Ольга', 'balance': '812394756'},
    {'key': 'GTBVS90', 'name': 'Максим', 'balance': '473829105'},
    {'key': 'HUCWT23', 'name': 'Татьяна', 'balance': '926518430'},
    {'key': 'IVDXU56', 'name': 'Алексей', 'balance': '358147296'},
    {'key': 'JWEYV89', 'name': 'Мария', 'balance': '647291853'},
]


class HashTable:
    def __init__(self, size):
        self.size = size
        self.slots = [None] * self.size
        self.used = 0
        self.collision = 0
        self.choice_append_table = None
        self.choice_hash_func = None

    def hash_func_select(self, choice_hash_func, key):
        if choice_hash_func == 1:
            return hash_polynomial(key, self.size)
        elif choice_hash_func == 2:
            return hash_FNV1a(key, self.size)
        elif choice_hash_func == 3:
            return hash_Dan_Bernstein(key, self.size)
        else:
            raise ValueError('Неизвестный номер хэш-функции')

    def append_hash_table(self, data):
        key = data['key']
        index = self.hash_func_select(self.choice_hash_func, key)

        if self.choice_append_table == 1:
            self.collision = append_chaining(self.slots, data, index, self.collision)
        elif self.choice_append_table == 2:
            self.collision = append_linear_probing(self.slots, data, index, self.collision)
        elif self.choice_append_table == 3:
            self.collision = append_quadratic_probing(self.slots, data, index, self.collision)
        else:
            raise ValueError("Неизвестный метод разрешения коллизий")

        self.used += 1

    def build(self, choice_append_table, choice_hash_func, items):
        self.choice_append_table = choice_append_table
        self.choice_hash_func = choice_hash_func
        for item in items:
            self.append_hash_table(choice_append_table, choice_hash_func, item)

    def get_rows_of_hash_table(self):
        rows = []
        for i, slot in enumerate(self.slots):
            if slot is None:
                rows.append({'slot': i, 'name': '', 'balance': '', '_role': 'empty'})
                continue

            if self.choice_append_table == 1:
                chain_length = len(slot)
                for j, item in enumerate(slot):
                    if chain_length == 1:
                        role = 'single'
                    elif j == 0:
                        role = 'start'
                    else:
                        role = 'continue'

                    rows.append({
                        'slot': i if j == 0 else '',
                        'name': item['name'],
                        'balance': item['balance'],
                        '_role': role,
                    })

            else:
                rows.append({
                    'slot': i,
                    'name': slot['name'],
                    'balance': slot['balance'],
                    '_role': 'single',
                })

        return rows

    def get_styled_data(self):
      rows = self.get_rows_of_hash_table()
      df = pd.DataFrame(rows, columns=['slot', 'name', 'balance', '_role'])

      def highlight(row):
         role = row['_role']
         if role == "single":
               return ['background-color: #c8e6c9'] * len(row)   # зелёный
         if role == "start":
               return ['background-color: #ffcdd2'] * len(row)   # красный
         if role == "continue":
               return ['background-color: #fff9c4'] * len(row)   # жёлтый
         if role == "empty":
               return ['background-color: #f5f5f5; color: #999'] * len(row)  # серый
         return [''] * len(row)

      styler = df.style.apply(highlight, axis=1)
      styler = styler.hide(axis='columns', subset=['_role'])
      return styler