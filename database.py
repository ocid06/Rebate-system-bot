import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("data.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    # ================= CREATE TABLE =================
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

    # ================= INSERT CLIENT =================
    def insert_client(self, account="", email="", nama=""):
        account = (account or "").strip()
        email = (email or "").strip().lower()
        nama = (nama or "").strip()

        # bersihin data
        if account.endswith(".0"):
            account = account[:-2]

        account = account.replace(" ", "")

        if account == "nan":
            account = ""
        if email == "nan":
            email = ""

        # jangan simpan kosong semua
        if not account and not email:
            return

        # ================= CEK DUPLIKAT =================
        self.cursor.execute("""
        SELECT id FROM clients
        WHERE account=? OR email=?
        """, (account, email))

        exists = self.cursor.fetchone()

        if exists:
            return  # skip kalau sudah ada

        # ================= INSERT =================
        self.cursor.execute("""
        INSERT INTO clients (account, email, nama)
        VALUES (?, ?, ?)
        """, (account, email, nama))

        self.conn.commit()

    # ================= SEARCH =================
    def find_client(self, keyword):
        keyword = (keyword or "").strip().lower()
        keyword = keyword.replace(" ", "")

        q = f"%{keyword}%"

        self.cursor.execute("""
        SELECT * FROM clients WHERE
        LOWER(account) LIKE ? OR
        LOWER(email) LIKE ? OR
        LOWER(nama) LIKE ?
        """, (q, q, q))

        return self.cursor.fetchall()

    # ================= COUNT =================
    def count_all(self):
        self.cursor.execute("SELECT COUNT(*) FROM clients")
        return self.cursor.fetchone()[0]

    # ================= DELETE ALL (OPTIONAL) =================
    def reset(self):
        self.cursor.execute("DELETE FROM clients")
        self.conn.commit()