import requests
import asyncio
import urllib3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

# Tắt cảnh báo InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# ID người dùng cho phép sử dụng /fl3 (chỉ bạn sử dụng)
ALLOWED_USER_ID = 5736655322

# ID nhóm cho phép sử dụng bot
ALLOWED_GROUP_ID = -1002221629819

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra nếu bot được gọi trong đúng nhóm
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn không thể sử dụng lệnh này ở đây.")
        return

    await update.message.reply_text(
        "Xin chào! Tôi là bot hỗ trợ tăng follow TikTok.\n\n"
        "Các lệnh bạn có thể sử dụng:\n"
        "/fl1 <username> - Tăng follow bằng API 1\n"
        "/fl2 <username> - Tăng follow bằng API 2\n"
        "/fl3 <username> - Tăng follow bằng API 3 (chỉ bạn có thể sử dụng)\n\n"
        "Chúc bạn sử dụng bot vui vẻ!"
    )

# Hàm xử lý tăng follow
async def fl(update: Update, context: ContextTypes.DEFAULT_TYPE, endpoint: str):
    # Kiểm tra nếu bot được gọi trong đúng nhóm
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn không thể sử dụng lệnh này ở đây.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /fl1 username")
        return
    
    username = context.args[0]
    url = f"https://nvp310107.x10.mx/{endpoint}?username={username}&key={API_KEY}"

    try:
        # Gửi yêu cầu đến API
        response = requests.get(url, headers=HEADERS, timeout=150, verify=False)

        # In ra toàn bộ dữ liệu trả về từ API để kiểm tra
        print("Dữ liệu API trả về:", response.text)

        try:
            data = response.json()
        except Exception:
            await update.message.reply_text("API trả về lỗi hoặc server đang bảo trì, vui lòng thử lại sau.")
            return

        # Kiểm tra xem API trả về dữ liệu hợp lệ
        if not isinstance(data, dict):
            await update.message.reply_text("API trả về dữ liệu không hợp lệ.")
            return

        # Kiểm tra các trường dữ liệu
        uid = data.get('uid', 'N/A')
        nickname = data.get('nickname', 'N/A')
        start_follow = data.get('start_follow', 'N/A')
        added_follow = data.get('added_follow', 'N/A')
        current_follow = data.get('current_follow', 'N/A')

        # Nếu dữ liệu không có hoặc trả về N/A, thông báo lỗi
        if uid == 'N/A' or nickname == 'N/A' or start_follow == 'N/A' or added_follow == 'N/A' or current_follow == 'N/A':
            await update.message.reply_text("Dữ liệu không hợp lệ hoặc API không trả về thông tin chính xác.")
            return

        message = (
            f"Tăng follow thành công cho: {username}\n\n"
            f"Thông Tin Tài Khoản:\n"
            f"UID: {uid}\n"
            f"Nick Name: {nickname}\n\n"
            f"FOLLOW BAN ĐẦU: {start_follow}\n"
            f"FOLLOW ĐÃ TĂNG: {added_follow}\n"
            f"FOLLOW HIỆN TẠI: {current_follow}"
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

# Lệnh /fl3 chỉ cho phép người dùng có ID 5736655322 sử dụng
async def fl3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra nếu bot được gọi trong đúng nhóm
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn không thể sử dụng lệnh này ở đây.")
        return

    # Kiểm tra nếu người dùng không phải là người cho phép
    if update.message.from_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /fl3 username")
        return
    
    username = context.args[0]
    url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"

    try:
        # Gửi yêu cầu đến API
        response = requests.get(url, headers=HEADERS, timeout=150, verify=False)

        # In ra toàn bộ dữ liệu trả về từ API để kiểm tra
        print("Dữ liệu API trả về:", response.text)

        try:
            data = response.json()
        except Exception:
            await update.message.reply_text("API trả về lỗi hoặc server đang bảo trì, vui lòng thử lại sau.")
            return

        # Kiểm tra xem API trả về dữ liệu hợp lệ
        if not isinstance(data, dict):
            await update.message.reply_text("API trả về dữ liệu không hợp lệ.")
            return

        # Kiểm tra các trường dữ liệu
        uid = data.get('uid', 'N/A')
        nickname = data.get('nickname', 'N/A')
        start_follow = data.get('start_follow', 'N/A')
        added_follow = data.get('added_follow', 'N/A')
        current_follow = data.get('current_follow', 'N/A')

        # Nếu dữ liệu không có hoặc trả về N/A, thông báo lỗi
        if uid == 'N/A' or nickname == 'N/A' or start_follow == 'N/A' or added_follow == 'N/A' or current_follow == 'N/A':
            await update.message.reply_text("Dữ liệu không hợp lệ hoặc API không trả về thông tin chính xác.")
            return

        message = (
            f"Tăng follow thành công cho: {username}\n\n"
            f"Thông Tin Tài Khoản:\n"
            f"UID: {uid}\n"
            f"Nick Name: {nickname}\n\n"
            f"FOLLOW BAN ĐẦU: {start_follow}\n"
            f"FOLLOW ĐÃ TĂNG: {added_follow}\n"
            f"FOLLOW HIỆN TẠI: {current_follow}"
        )

        await update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Không kết nối được đến server: {e}")

# Chạy bot
def main():
    keep_alive()  # giữ bot luôn online

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  # Lệnh /start
    app.add_handler(CommandHandler("fl1", fl1))     # Lệnh /fl1
    app.add_handler(CommandHandler("fl2", fl2))     # Lệnh /fl2
    app.add_handler(CommandHandler("fl3", fl3))     # Lệnh /fl3 (chỉ bạn có thể sử dụng)

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
