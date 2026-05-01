import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("data.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker TEXT,
            nomor_akun_trading TEXT,
            nama TEXT,
            email TEXT,
            UNIQUE(nomor_akun_trading, broker)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rebates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_akun_trading TEXT,
            rebate REAL
        )
        """)

        self.conn.commit()

    def upsert_client(self, data):
        akun = data["nomor_akun_trading"]
        broker = data["broker"]

        self.cursor.execute("""
        SELECT id FROM clients WHERE nomor_akun_trading=? AND broker=?
        """, (akun, broker))

        existing = self.cursor.fetchone()

        if existing:
            self.cursor.execute("""
            UPDATE clients SET nama=?, email=? WHERE id=?
            """, (data["nama"], data["email"], existing[0]))
        else:
            self.cursor.execute("""
            INSERT INTO clients (broker, nomor_akun_trading, nama, email)
            VALUES (?, ?, ?, ?)
            """, (broker, akun, data["nama"], data["email"]))

        self.conn.commit()

    def insert_rebate(self, akun, rebate):
        self.cursor.execute("""
        INSERT INTO rebates (nomor_akun_trading, rebate)
        VALUES (?, ?)
        """, (akun, rebate))
        self.conn.commit()

    def get_total_rebate(self, akun):
        self.cursor.execute("""
        SELECT SUM(rebate) FROM rebates WHERE nomor_akun_trading=?
        """, (akun,))
        result = self.cursor.fetchone()[0]
        return result or 0