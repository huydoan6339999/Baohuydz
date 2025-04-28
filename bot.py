import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

# BOT TOKEN
BOT_TOKEN = '6374595640:AAEBURXySkM_YWTI2xk988NpkIa3wQ_xNq8'

# API Key
API_KEY = '30T42025VN'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là bot hỗ trợ tăng follow TikTok.\n\n"
        "Các lệnh bạn có thể sử dụng:\n"
        "/fl1 <username> - Tăng follow bằng API 1\n"
        "/fl2 <username> - Tăng follow bằng API 2\n\n"
        "Chúc bạn sử dụng bot vui vẻ!"
    )

# Hàm xử lý tăng follow
async def fl(update: Update, context: ContextTypes.DEFAULT_TYPE, endpoint: str):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /fl1 username")
        return
    
    username = context.args[0]
    url = f"https://nvp310107.x10.mx/{endpoint}?username={username}&key={API_KEY}"

    try:
        # Thêm verify=False để bỏ qua kiểm tra SSL
        response = requests.get(url, headers=HEADERS, timeout=10, verify=False)

        try:
            data = response.json()
        except Exception:
            await update.message.reply_text("API trả về lỗi hoặc server đang bảo trì, vui lòng thử lại sau.")
            return

        if not isinstance(data, dict):
            await update.message.reply_text("API trả về dữ liệu không hợp lệ.")
            return

        message = (
            f"Tăng follow thành công cho: {username}\n\n"
            f"Thông Tin Tài Khoản:\n"
            f"UID: {data.get('uid', 'N/A')}\n"
            f"Nick Name: {data.get('nickname', 'N/A')}\n\n"
            f"FOLLOW BAN ĐẦU: {data.get('start_follow', 'N/A')}\n"
            f"FOLLOW ĐÃ TĂNG: {data.get('added_follow', 'N/A')}\n"
            f"FOLLOW HIỆN TẠI: {data.get('current_follow', 'N/A')}"
        )

        await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Không kết nối được đến server: {e}")

# Lệnh /fl1
async def fl1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fl(update, context, "fltikfam.php")

# Lệnh /fl2
async def fl2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fl(update, context, "fltik.php")

# Chạy bot
def main():
    keep_alive()  # giữ bot luôn online

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  # Lệnh /start
    app.add_handler(CommandHandler("fl1", fl1))     # Lệnh /fl1
    app.add_handler(CommandHandler("fl2", fl2))     # Lệnh /fl2

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
