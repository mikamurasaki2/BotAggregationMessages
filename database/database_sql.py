import sqlite3 as sq


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sq.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        print("def create1")
        columns_str = ', '.join([f'{name} {data_type}' for name, data_type in columns])
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})')
        print("def create2")
        self.conn.commit()
        print("def create3")

    def insert_data(self, table_name, data):
        print("def insert1")
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f'?' for _ in data.values()])
        values = tuple(data.values())
        print("def insert2")
        self.cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
        print("def insert3")
        self.conn.commit()
        print("def insert4")

    # Проверка существования значения в таблице
    def check_value(self, table_name, field, value):
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,))
        result = self.cursor.fetchone()
        if result is None:
            return True
        else:
            return False

    def fetch_data(self, table_name, condition=None):
        print("def fetch1")
        query = f'SELECT * FROM {table_name}'
        if condition:
            query += f' WHERE{condition}'
        print("def fetch2")
        self.cursor.execute(query)
        print("def fetch3")
        return self.cursor.fetchall()

    def close_connection(self):
        print("def Close1")
        self.conn.close()
        print("def Close2")