import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("data.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT,
            email TEXT,
            nama TEXT
        )
        """)
        self.conn.commit()

    def insert_client(self, account="", email="", nama=""):
        self.cursor.execute("""
        INSERT INTO clients (account, email, nama)
        VALUES (?, ?, ?)
        """, (account, email, nama))
        self.conn.commit()

    def find_client(self, keyword):
        q = f"%{keyword}%"

        self.cursor.execute("""
        SELECT * FROM clients WHERE
        account LIKE ? OR email LIKE ? OR nama LIKE ?
        """, (q, q, q))

        return self.cursor.fetchall()