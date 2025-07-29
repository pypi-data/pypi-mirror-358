# -*- coding:utf-8 -*-
import sqlite3


class UtilDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def __del__(self):
        try:
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            del e

    def get_tables_name(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        return [i[0] for i in tables]

    def get_table_title(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        titles = self.cursor.fetchall()
        print(titles)

    def insert_data_to_table(self, table_name, columns, values):
        columns = ",".join(columns)
        values = ",".join(values)
        self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")

    def del_data_from_table(self, table_name, title, value):
        self.cursor.execute(f"DELETE from {table_name} where {title} = {value}")

    def get_table_info(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()
