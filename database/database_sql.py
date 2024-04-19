import sqlite3 as sq


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sq.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        columns_str = ', '.join([f'{name} {data_type}' for name, data_type in columns])
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})')
        self.conn.commit()

    def insert_data(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f'?' for _ in data.values()])
        values = tuple(data.values())
        self.cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
        self.conn.commit()

    # Проверка существования значения в таблице
    def check_value(self, table_name, field, value):
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,))
        result = self.cursor.fetchone()
        if result is None:
            return True
        else:
            return False

    def fetch_data(self, table_name, condition=None):
        query = f'SELECT * FROM {table_name}'
        if condition:
            query += f' WHERE{condition}'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()

    def delete_user(self, table_name, field, value):
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,))
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute("DELETE FROM " + table_name + " WHERE " + field + " = ?", (value,))
            self.conn.commit()
            return True  # Indicates the user was found and deleted
        else:
            return False  # Indicates the user was not found

    def get_value(self, table_name, field, value):
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + field + " = ?", (value,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    #
    # def get_last_name(user_id):
    #     with get_db() as db:
    #         user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
    #         if user:
    #             return user.user_last_name
    #         else:
    #             return None
    #
    # def get_user_id(user_id):
    #     with get_db() as db:
    #         user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
    #         if user:
    #             return user.user_id
    #         else:
    #             return None
    #
    # # Удалить пользователя
    # def delete_user(user_id):
    #     with get_db() as db:
    #         user = db.query(models.PrivateUser).filter(models.PrivateUser.user_id == user_id).first()
    #         if user:
    #             db.delete(user)
    #             db.commit()
    #             return True
    #         else:
    #             return False