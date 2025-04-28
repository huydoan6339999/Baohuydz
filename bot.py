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

# ID nhóm Telegram được phép sử dụng bot
ALLOWED_GROUP_ID = -1002221629819

# ID người được phép dùng /fl3
ALLOWED_USER_ID = 5736655322

# Header giả lập trình duyệt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

# Biến lưu các task treo tự động
treo_fl3_tasks = {}

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là bot hỗ trợ tăng follow TikTok.\n\n"
        "Các lệnh:\n"
        "/fl1 <username> - Tăng follow API 1\n"
        "/fl2 <username> - Tăng follow API 2\n"
        "/fl3 <username> - Tăng follow API 3 (tự động treo 15 phút)\n"
        "/huytreo3 <username> - Hủy treo tăng follow\n\n"
        "Lưu ý: Chỉ dùng được trong nhóm và /fl3 chỉ bạn được phép dùng."
    )

# Hàm xử lý tăng follow chung
async def fl(update: Update, context: ContextTypes.DEFAULT_TYPE, endpoint: str):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn chỉ có thể dùng bot trong nhóm được phép.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /fl1 username")
        return
    
    username = context.args[0]
    url = f"https://nvp310107.x10.mx/{endpoint}?username={username}&key={API_KEY}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=300, verify=False)
        data = response.json()
        
        if not isinstance(data, dict):
            await update.message.reply_text("API trả về dữ liệu không hợp lệ.")
            return

        uid = data.get('uid', 'N/A')
        nickname = data.get('nickname', 'N/A')
        start_follow = data.get('start_follow', 'N/A')
        added_follow = data.get('added_follow', 'N/A')
        current_follow = data.get('current_follow', 'N/A')

        if uid == 'N/A' or nickname == 'N/A':
            await update.message.reply_text("Dữ liệu tài khoản không hợp lệ.")
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
        await update.message.reply_text(f"Không kết nối được server: {e}")

# Lệnh /fl1
async def fl1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fl(update, context, "fltikfam.php")

# Lệnh /fl2
async def fl2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fl(update, context, "fltik.php")

# Lệnh /fl3 - Tự động treo
async def fl3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn chỉ có thể dùng bot trong nhóm được phép.")
        return

    if update.message.from_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /fl3 username")
        return
    
    username = context.args[0]

    if username in treo_fl3_tasks:
        await update.message.reply_text(f"Đã bắt đầu treo tăng follow cho {username} rồi.")
        return

    await update.message.reply_text(f"Đã bắt đầu treo tăng follow cho {username} mỗi 15 phút.")

    async def auto_treo():
        while True:
            url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"
            try:
                response = requests.get(url, headers=HEADERS, timeout=300, verify=False)
                data = response.json()

                if not isinstance(data, dict):
                    await update.message.reply_text(f"Lỗi dữ liệu API khi tăng follow cho {username}.")
                    break

                message = (
                    f"Tăng follow tự động cho: {username}\n"
                    f"UID: {data.get('uid', 'N/A')}\n"
                    f"Nick Name: {data.get('nickname', 'N/A')}\n"
                    f"FOLLOW BAN ĐẦU: {data.get('start_follow', 'N/A')}\n"
                    f"FOLLOW ĐÃ TĂNG: {data.get('added_follow', 'N/A')}\n"
                    f"FOLLOW HIỆN TẠI: {data.get('current_follow', 'N/A')}"
                )
                await update.message.reply_text(message)

            except Exception as e:
                await update.message.reply_text(f"Lỗi API khi treo follow {username}: {e}")
            
            await asyncio.sleep(900)  # 15 phút

    task = asyncio.create_task(auto_treo())
    treo_fl3_tasks[username] = task

# Lệnh /huytreo3 - Hủy treo
async def huytreo3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn chỉ có thể dùng bot trong nhóm được phép.")
        return

    if update.message.from_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username cần hủy treo.\nVí dụ: /huytreo3 username")
        return

    username = context.args[0]

    if username in treo_fl3_tasks:
        treo_fl3_tasks[username].cancel()
        del treo_fl3_tasks[username]
        await update.message.reply_text(f"Đã hủy treo tăng follow cho {username}.")
    else:
        await update.message.reply_text(f"Không tìm thấy treo nào cho {username}.")

# Main chạy bot
def main():
    keep_alive()  # Giữ server luôn online

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fl1", fl1))
    app.add_handler(CommandHandler("fl2", fl2))
    app.add_handler(CommandHandler("fl3", fl3))
    app.add_handler(CommandHandler("huytreo3", huytreo3))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
