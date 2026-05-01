import pandas as pd
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Database

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak terbaca")

db = Database()


# ================= FILE READER =================
def read_file(file_name):
    df = None

    # CSV utf-8
    try:
        df = pd.read_csv(file_name, encoding="utf-8", on_bad_lines="skip")
        return df
    except:
        pass

    # CSV latin
    try:
        df = pd.read_csv(file_name, encoding="latin1", on_bad_lines="skip")
        return df
    except:
        pass

    # CSV delimiter ;
    try:
        df = pd.read_csv(file_name, delimiter=";", encoding="latin1", on_bad_lines="skip")
        return df
    except:
        pass

    # auto detect
    try:
        df = pd.read_csv(file_name, sep=None, engine="python", on_bad_lines="skip")
        return df
    except:
        pass

    # Excel paksa
    try:
        df = pd.read_excel(file_name, engine="openpyxl")
        return df
    except:
        pass

    return None


# ================= UPLOAD FILE =================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("📥 FILE MASUK")

        file = await update.message.document.get_file()
        file_name = update.message.document.file_name

        # FIX nama file aneh
        file_name = file_name.replace(".csv.xlsx", ".csv")

        await file.download_to_drive(file_name)

        df = read_file(file_name)

        if df is None:
            await update.message.reply_text("❌ File tidak bisa dibaca")
            return

        print("COLUMNS:", df.columns.tolist())
        print(df.head())

        df.columns = [c.lower().strip() for c in df.columns]

        inserted = 0

        # ================= PARSER =================
        for _, row in df.iterrows():
            account = ""
            email = ""
            nama = ""

            for col in df.columns:
                val = str(row[col]).strip()

                if not val or val.lower() == "nan":
                    continue

                # EMAIL
                if "@" in val:
                    email = val.lower()

                # ACCOUNT
                elif val.replace(".", "").isdigit():
                    val_clean = val.replace(".0", "").replace(" ", "")
                    if len(val_clean) >= 5:
                        account = val_clean

                # NAMA
                elif any(c.isalpha() for c in val) and len(val) > 3:
                    nama = val

            if account or email:
                db.insert_client(account, email, nama)
                inserted += 1

        await update.message.reply_text(f"✅ {inserted} data client masuk")

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text(f"❌ Error: {e}")


# ================= CEK =================
async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("🔍 CEK DIPANGGIL")

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

    except Exception as e:
        print("ERROR CEK:", e)
        await update.message.reply_text("❌ Error saat cek")


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Validasi Client FXPayout\n\n"
        "📤 Upload CSV / Excel\n"
        "🔍 /cek <data>"
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