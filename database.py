import psycopg2
import os

class Database:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
raise ValueError("DATABASE_URL belum masuk ke Railway")

if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        self.conn = psycopg2.connect(db_url)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            account TEXT,
            email TEXT,
            nama TEXT
        )
        """)
        self.conn.commit()

    def insert_client(self, account, email, nama):
        self.cursor.execute("""
        INSERT INTO clients (account, email, nama)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        """, (account, email, nama))
        self.conn.commit()

    def find_client(self, keyword):
        q = f"%{keyword}%"
        self.cursor.execute("""
        SELECT * FROM clients WHERE
        account ILIKE %s OR
        email ILIKE %s OR
        nama ILIKE %s
        """, (q, q, q))
        return self.cursor.fetchall()