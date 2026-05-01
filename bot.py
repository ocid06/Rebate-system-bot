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
    await file.download_to_drive("data.csv")

    df = pd.read_csv("data.csv")

    # DEBUG: lihat nama kolom
    print("COLUMNS:", df.columns.tolist())

    # normalisasi nama kolom
    df.columns = [c.lower().strip() for c in df.columns]

    account_col = None
    email_col = None
    name_col = None

    # ================= DETECT KOLOM =================
    for col in df.columns:
        if any(k in col for k in ["account", "login", "wallet", "id", "uid"]):
            account_col = col

        if "email" in col:
            email_col = col

        if any(k in col for k in ["name", "nama"]):
            name_col = col

    # ================= VALIDASI =================
    if not account_col and not email_col:
        await update.message.reply_text(
            f"❌ Kolom tidak dikenali\n\nKolom:\n{df.columns.tolist()}"
        )
        return

    inserted = 0

    # ================= INSERT =================
    for _, row in df.iterrows():
        account = str(row[account_col]).strip() if account_col else ""
        email = str(row[email_col]).strip() if email_col else ""
        nama = str(row[name_col]).strip() if name_col else ""

        # bersihin data
        if account == "nan":
            account = ""
        if email == "nan":
            email = ""

        if account.endswith(".0"):
            account = account[:-2]

        account = account.replace(" ", "")

        if account or email:
            db.insert_client(account, email, nama)
            inserted += 1

    await update.message.reply_text(f"✅ {inserted} data client masuk")
# ================= CEK CLIENT =================
async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /cek email / akun / nama")
        return

    keyword = context.args[0]

    results = db.find_client(keyword)

    if not results:
        await update.message.reply_text("❌ Tidak terdaftar di IB FXPayout")
        return

    text = "✅ TERDAFTAR DI IB FXPAYOUT\n\n"

    for r in results:
        text += f"Akun: {r[1]}\nEmail: {r[2]}\nNama: {r[3]}\n\n"

    await update.message.reply_text(text)

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CommandHandler("cek", cek))

    print("Bot validasi jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()