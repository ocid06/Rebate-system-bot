import pandas as pd
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Database

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak terbaca")

db = Database()

# ================= UPLOAD CSV =================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name.lower()

    # download sekali saja
    await file.download_to_drive(file_name)

    # ================= DETECT FORMAT =================
    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(file_name)

        elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            df = pd.read_excel(file_name)

        elif file_name.endswith(".txt"):
            df = pd.read_csv(file_name, delimiter=";")

        else:
            await update.message.reply_text("❌ Format file tidak didukung")
            return

    except Exception as e:
        await update.message.reply_text(f"❌ Gagal membaca file: {e}")
        return

    # ================= DEBUG =================
    print("COLUMNS:", df.columns.tolist())

    df.columns = [c.lower().strip() for c in df.columns]

    inserted = 0

    # ================= SMART PARSER =================
    for _, row in df.iterrows():
        account = ""
        email = ""
        nama = ""

        for col in df.columns:
            val = str(row[col]).strip()

            if val.lower() == "nan" or val == "":
                continue

            # EMAIL
            if "@" in val:
                email = val

            # ACCOUNT (angka panjang)
            elif val.replace(".", "").isdigit():
                account = val.replace(".0", "")

            # NAMA
            elif any(c.isalpha() for c in val) and len(val) > 3:
                nama = val

        if account or email:
            db.insert_client(account, email, nama)
            inserted += 1

    await update.message.reply_text(f"✅ {inserted} data client masuk")