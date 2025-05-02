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

# API gốc
API_URL = 'https://api.thanhtien.site/lynk/dino/telefl.php'

# ID nhóm Telegram được phép sử dụng bot
ALLOWED_GROUP_ID = -1002221629819

# ID admin chính (chỉ người này mới được dùng /adduser)
ALLOWED_USER_ID = 5736655322

# Danh sách user được phép dùng lệnh /buff2
ALLOWED_USERS = {5736655322}

# Biến lưu các task treo tự động
buff2_tasks = {}

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là bot hỗ trợ tăng follow TikTok.\n\n"
        "Các lệnh:\n"
        "/fl2 <username> - Tăng follow API 2\n"
        "/buff2 <username> - Buff auto 15 phút\n"
        "/huytreo2 <username> - Hủy buff\n"
        "/adduser <id> - Thêm user dùng được /buff2 (chỉ admin)"
    )

# Lệnh /fl2
async def fl2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn chỉ có thể dùng bot trong nhóm được phép.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /fl2 username")
        return

    username = context.args[0]
    url = f"{API_URL}?user={username}&userid={update.message.from_user.id}&tokenbot={BOT_TOKEN}"

    try:
        response = requests.get(url, timeout=30, verify=False)
        data = response.json()

        if not isinstance(data, dict):
            await update.message.reply_text("API trả về dữ liệu không hợp lệ.")
            return

        message = (
            f"Tăng follow cho: {username}\n"
            f"UID: {data.get('uid', 'N/A')}\n"
            f"Nick Name: {data.get('nickname', 'N/A')}\n"
            f"FOLLOW BAN ĐẦU: {data.get('start_follow', 'N/A')}\n"
            f"FOLLOW ĐÃ TĂNG: {data.get('added_follow', 'N/A')}\n"
            f"FOLLOW HIỆN TẠI: {data.get('current_follow', 'N/A')}"
        )
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Lỗi kết nối API: {e}")

# Lệnh /buff2
async def buff2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn chỉ có thể dùng bot trong nhóm được phép.")
        return

    if update.message.from_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username.\nVí dụ: /buff2 username")
        return

    username = context.args[0]

    if username in buff2_tasks:
        await update.message.reply_text(f"Đã bắt đầu buff cho {username} rồi.")
        return

    await update.message.reply_text(f"Đã bắt đầu buff follow cho {username} mỗi 15 phút.")

    async def auto_buff():
        while True:
            url = f"{API_URL}?user={username}&userid={update.message.from_user.id}&tokenbot={BOT_TOKEN}"
            try:
                response = requests.get(url, timeout=30, verify=False)
                data = response.json()

                if not isinstance(data, dict):
                    await update.message.reply_text(f"Lỗi dữ liệu API khi buff cho {username}.")
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
                await update.message.reply_text(f"Lỗi API khi buff {username}: {e}")

            await asyncio.sleep(900)  # 15 phút

    task = asyncio.create_task(auto_buff())
    buff2_tasks[username] = task

# Lệnh /huytreo2
async def huytreo2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("Bạn chỉ có thể dùng bot trong nhóm được phép.")
        return

    if update.message.from_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập username cần hủy.\nVí dụ: /huytreo2 username")
        return

    username = context.args[0]

    if username in buff2_tasks:
        buff2_tasks[username].cancel()
        del buff2_tasks[username]
        await update.message.reply_text(f"Đã hủy buff cho {username}.")
    else:
        await update.message.reply_text(f"Không tìm thấy buff nào cho {username}.")

# Lệnh /adduser <id>
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập ID người dùng cần thêm.\nVí dụ: /adduser 123456789")
        return

    try:
        new_id = int(context.args[0])
        ALLOWED_USERS.add(new_id)
        await update.message.reply_text(f"Đã thêm user ID {new_id} vào danh sách sử dụng lệnh /buff2.")
    except ValueError:
        await update.message.reply_text("ID không hợp lệ.")

# Main chạy bot
def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fl2", fl2))
    app.add_handler(CommandHandler("buff2", buff2))
    app.add_handler(CommandHandler("huytreo2", huytreo2))
    app.add_handler(CommandHandler("adduser", adduser))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
