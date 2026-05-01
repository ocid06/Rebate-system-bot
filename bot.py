import pandas as pd
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Database

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak terbaca")

db = Database()

# ================= UPLOAD FILE =================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name.lower()

        # download file
        await file.download_to_drive(file_name)

        # ================= DETECT FORMAT =================
        if file_name.endswith(".csv"):
            df = pd.read_csv(file_name)

        elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            df = pd.read_excel(file_name)

        else:
            await update.message.reply_text("❌ Format tidak didukung")
            return

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
                    email = val.lower()

                # ACCOUNT (angka panjang)
                elif val.replace(".", "").isdigit() and len(val) >= 5:
                    account = val.replace(".0", "").replace(" ", "")

                # NAMA
                elif any(c.isalpha() for c in val) and len(val) > 3:
                    nama = val

            if account or email:
                db.insert_client(account, email, nama)
                inserted += 1

        await update.message.reply_text(f"✅ {inserted} data client masuk")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ================= CEK CLIENT =================
async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /cek email / akun / nama")
        return

    keyword = context.args[0].lower().strip()

    results = db.find_client(keyword)

    if not results:
        await update.message.reply_text("❌ Tidak terdaftar di IB FXPayout")
        return

    text = "✅ TERDAFTAR DI IB FXPAYOUT\n\n"

    for r in results:
        text += f"Akun: {r[1]}\nEmail: {r[2]}\nNama: {r[3]}\n\n"

    await update.message.reply_text(text)


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Validasi Client FXPayout\n\n"
        "📤 Upload CSV / Excel broker\n"
        "🔍 /cek <email / akun / nama>"
    )


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cek", cek))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("🤖 Bot jalan...")
    app.run_polling()


if __name__ == "__main__":
    main()