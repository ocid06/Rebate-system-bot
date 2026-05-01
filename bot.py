import re
import pandas as pd
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Database

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak terbaca dari environment!")

db = Database()

# ================= PARSE =================
def parse_text(text):
    text = text.lower()

    def ambil(label):
        match = re.search(rf"{label}\s*:\s*(.+)", text)
        return match.group(1).strip() if match else ""

    return {
        "broker": ambil("broker"),
        "nomor_akun_trading": ambil("nomor akun trading"),
        "nama": ambil("nama lengkap"),
        "email": ambil("email"),
    }

# ================= INPUT CLIENT =================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    data = parse_text(text)

    if not data["nomor_akun_trading"]:
        return

    db.upsert_client(data)

    await update.message.reply_text("✅ Client disimpan")

# ================= UPLOAD REBATE =================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    await file.download_to_drive("rebate.csv")

    df = pd.read_csv("rebate.csv")
    df.columns = [c.lower() for c in df.columns]

    account_col = None
    rebate_col = None

    for col in df.columns:
        if "account" in col or "login" in col:
            account_col = col

        if "rebate" in col or "commission" in col or "profit" in col:
            rebate_col = col

    inserted = 0

    for _, row in df.iterrows():
        akun = str(row[account_col])
        rebate = float(row[rebate_col])

        if akun:
            db.insert_rebate(akun, rebate)
            inserted += 1

    await update.message.reply_text(f"✅ {inserted} rebate masuk")

# ================= REBATE COMMAND =================
async def rebate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /rebate 123456 atau email")
        return

    keyword = context.args[0]

    accounts = db.find_accounts(keyword)

    if not accounts:
        await update.message.reply_text("❌ Data tidak ditemukan")
        return

    total = 0

    for acc in accounts:
        total += db.get_total_rebate(acc)

    final = total * 0.7

    await update.message.reply_text(f"💰 ${final:.2f}")