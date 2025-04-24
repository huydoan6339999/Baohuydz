import json
import os
import logging
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from keep_alive import keep_alive  # Import keep_alive function
from dotenv import load_dotenv  # Thêm để tải biến môi trường từ tệp .env

# Tải biến môi trường
load_dotenv()  # Tải các biến từ .env file

# Lấy token từ biến môi trường
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # ID của admin cũng được lưu trong biến môi trường
DATA_FILE = "treo_data.json"
USER_FILE = "users_data.json"  # File để lưu người dùng

# Kiểm tra nếu các biến môi trường không được thiết lập
if not BOT_TOKEN or not ADMIN_ID:
    raise ValueError("BOT_TOKEN hoặc ADMIN_ID không được thiết lập trong môi trường!")

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Tải dữ liệu người dùng
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Lưu dữ liệu người dùng
def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# Dữ liệu người dùng: {user_id: username}
users = load_users()

# Kiểm tra nếu người dùng là admin
def is_admin(user_id):
    return str(user_id) == ADMIN_ID

# Gửi cảnh báo lỗi về admin
async def send_error_to_admin(message):
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = app.bot
    await bot.send_message(chat_id=ADMIN_ID, text=message)

# Kiểm tra các tên người dùng TikTok mỗi 15 phút
def check_usernames():
    for user_id, user_data in users.items():
        username = user_data.get("username", "")
        if not username:
            continue
        
        url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={BOT_TOKEN}"
        try:
            res = requests.get(url, timeout=30)  # timeout sau 30 giây
            logging.info(f"Checked @{username} for {user_id} - Status: {res.status_code}")
        except requests.exceptions.Timeout:
            error_message = f"Timeout khi check @{username} của {user_id}"
            logging.warning(error_message)
            send_error_to_admin(error_message)  # Gửi cảnh báo cho admin
        except Exception as e:
            error_message = f"Lỗi khi check @{username} của {user_id}: {e}"
            logging.error(error_message)
            send_error_to_admin(error_message)  # Gửi cảnh báo cho admin
        time.sleep(2)  # Delay 2 giây giữa mỗi lần gọi API

# Lệnh /adduser
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Bạn không có quyền thêm người dùng!")

    if not context.args:
        return await update.message.reply_text("Vui lòng nhập user_id của người dùng cần thêm. Ví dụ: /adduser <user_id>")

    user_id = context.args[0].strip()

    # Kiểm tra user_id có hợp lệ không
    if not user_id.isdigit():
        return await update.message.reply_text("User ID không hợp lệ, vui lòng nhập user_id dạng số!")

    if user_id in users:
        return await update.message.reply_text(f"Người dùng {user_id} đã có trong danh sách.")
    
    # Thêm người dùng vào danh sách
    users[user_id] = {"username": "Unknown"}  # Bạn có thể cập nhật tên người dùng nếu cần
    save_users(users)
    await update.message.reply_text(f"Đã thêm người dùng {user_id} vào danh sách!")

# Lệnh /listusers để xem danh sách người dùng
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Bạn không có quyền xem danh sách người dùng!")

    if not users:
        return await update.message.reply_text("Danh sách người dùng trống.")
    
    text = "\n".join([f"User ID: {uid}, Username: {data['username']}" for uid, data in users.items()])
    await update.message.reply_text(f"Danh sách người dùng:\n{text}")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Đây là các lệnh của bot:\n"
        "/adduser <user_id> - Thêm người dùng (chỉ admin)\n"
        "/listusers - Xem danh sách người dùng (chỉ admin)\n"
        "/fl <username> - Treo TikTok\n"
        "/huytreo - Hủy treo\n"
        "/list - Xem username đang treo"
    )

# Khởi chạy bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", add_user))  # Thêm lệnh /adduser
    app.add_handler(CommandHandler("listusers", list_users))  # Thêm lệnh /listusers

    # Tự động kiểm tra tên người dùng mỗi 15 phút
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_usernames, "interval", minutes=15)
    scheduler.start()

    logging.info("Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    keep_alive()  # Giữ bot luôn hoạt động
    asyncio.run(main())
