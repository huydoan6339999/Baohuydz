import json
import os
import logging
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from keep_alive import keep_alive
from dotenv import load_dotenv

# Tải biến môi trường từ .env (nếu có)
load_dotenv()

# Lấy biến môi trường
BOT_TOKEN = os.getenv("6320148381:AAEntoWHszOtVaRTBiPmxYNDyELNqxm-8Ag")
ADMIN_ID = os.getenv("5736655322")

# Kiểm tra và báo lỗi nếu thiếu
if not BOT_TOKEN:
    raise ValueError("LỖI: Thiếu biến môi trường BOT_TOKEN!")
if not ADMIN_ID:
    raise ValueError("LỖI: Thiếu biến môi trường ADMIN_ID!")

DATA_FILE = "treo_data.json"
USER_FILE = "users_data.json"

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load & Save user
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

users = load_users()

# Check admin
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

# Gửi lỗi cho admin
async def send_error_to_admin(message):
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.send_message(chat_id=ADMIN_ID, text=message)

# Auto check username TikTok mỗi 15 phút
def check_usernames():
    for user_id, user_data in users.items():
        username = user_data.get("username", "")
        if not username:
            continue

        url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={BOT_TOKEN}"
        try:
            res = requests.get(url, timeout=30)
            logging.info(f"Checked @{username} for {user_id} - Status: {res.status_code}")
        except requests.exceptions.Timeout:
            msg = f"Timeout khi check @{username} của {user_id}"
            logging.warning(msg)
            try: send_error_to_admin(msg)
            except: pass
        except Exception as e:
            msg = f"Lỗi khi check @{username} của {user_id}: {e}"
            logging.error(msg)
            try: send_error_to_admin(msg)
            except: pass
        time.sleep(2)

# Lệnh
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Bạn không có quyền thêm người dùng!")

    if not context.args:
        return await update.message.reply_text("Dùng: /adduser <user_id>")

    user_id = context.args[0].strip()
    if not user_id.isdigit():
        return await update.message.reply_text("User ID phải là số!")

    if user_id in users:
        return await update.message.reply_text(f"User {user_id} đã có.")

    users[user_id] = {"username": "Unknown"}
    save_users(users)
    await update.message.reply_text(f"Đã thêm user {user_id}!")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Bạn không có quyền!")

    if not users:
        return await update.message.reply_text("Không có user nào.")

    text = "\n".join([f"{uid}: {data['username']}" for uid, data in users.items()])
    await update.message.reply_text(f"User hiện tại:\n{text}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Các lệnh:\n"
        "/adduser <id>\n"
        "/listusers"
    )

# Main
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("listusers", list_users))

    scheduler = BackgroundScheduler()
    scheduler.add_job(check_usernames, "interval", minutes=15)
    scheduler.start()

    logging.info("Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    keep_alive()
    asyncio.run(main())
