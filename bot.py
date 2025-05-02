import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = '6374595640:AAEBURXySkM_YWTI2xk988NpkIa3wQ_xNq8'
ALLOWED_GROUP_ID = -1002221629819
ALLOWED_USER_ID = 5736655322
API_URL = 'https://api.thanhtien.site/lynk/dino/telefl.php'

buff2_tasks = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi là bot hỗ trợ tăng follow TikTok.\n\n"
        "Các lệnh:\n"
        "/buff2 <username> - Tăng follow tự động mỗi 15 phút\n"
        "/huybuff2 <username> - Hủy treo follow\n"
        "/adduser <id> - Cập nhật ID người dùng được phép"
    )

# /buff2
async def buff2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        return await update.message.reply_text("Lệnh chỉ dùng trong nhóm được phép.")
    
    if update.message.from_user.id != ALLOWED_USER_ID:
        return await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
    
    if not context.args:
        return await update.message.reply_text("Vui lòng nhập username. Ví dụ: /buff2 username")
    
    username = context.args[0]

    if username in buff2_tasks:
        return await update.message.reply_text(f"Đã bắt đầu treo tăng follow cho @{username}.")

    await update.message.reply_text(f"Đang treo tăng follow cho @{username} mỗi 15 phút.")

    async def auto_buff():
        while True:
            try:
                params = {
                    'user': username,
                    'userid': str(ALLOWED_USER_ID),
                    'tokenbot': BOT_TOKEN
                }
                res = requests.get(API_URL, params=params, timeout=20)
                data = res.json()

                status_text = "✅ Thành công" if data.get('status', False) else "❌ Thất bại"
                reply_text = (
                    f"🏖️ Khu Vực: {data.get('khu_vuc', 'N/A')}\n"
                    f"👤 Tên: {data.get('name', 'N/A')}\n"
                    f"🆔 User ID: {data.get('user_id', 'N/A')}\n"
                    f"📅 Ngày tạo: {data.get('create_time', 'N/A')}\n"
                    f"📌 Username: @{data.get('username', 'N/A')}\n"
                    f"👥 Followers (Trước): {data.get('followers_before', 0)}\n"
                    f"👥 Followers (Sau): {data.get('followers_after', 0)}\n"
                    f"✨ Đã thêm: {data.get('followers_add', 0)}\n"
                    f"💬 Thông báo: {data.get('message', '')}\n"
                    f"🔍 Trạng thái: {status_text}"
                )
                await update.message.reply_text(reply_text)
            except Exception as e:
                await update.message.reply_text(f"Lỗi API: {e}")
            await asyncio.sleep(900)  # Treo 15 phút

    task = asyncio.create_task(auto_buff())
    buff2_tasks[username] = task

# /huybuff2
async def huybuff2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        return await update.message.reply_text("Lệnh chỉ dùng trong nhóm được phép.")
    
    if update.message.from_user.id != ALLOWED_USER_ID:
        return await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
    
    if not context.args:
        return await update.message.reply_text("Vui lòng nhập username. Ví dụ: /huybuff2 username")
    
    username = context.args[0]

    if username in buff2_tasks:
        buff2_tasks[username].cancel()
        del buff2_tasks[username]
        await update.message.reply_text(f"Đã hủy treo tăng follow cho @{username}.")
    else:
        await update.message.reply_text(f"Không có treo nào cho @{username}.")

# /adduser <id>
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ALLOWED_USER_ID
    if update.message.from_user.id != ALLOWED_USER_ID:
        return await update.message.reply_text("Bạn không có quyền thay đổi người dùng được phép.")
    
    if not context.args:
        return await update.message.reply_text("Vui lòng nhập ID mới. Ví dụ: /adduser 123456789")
    
    try:
        ALLOWED_USER_ID = int(context.args[0])
        await update.message.reply_text(f"Đã đổi người dùng được phép sang: {ALLOWED_USER_ID}")
    except ValueError:
        await update.message.reply_text("ID không hợp lệ. Vui lòng nhập số.")

# Main
def main():
    keep_alive()  # Giữ server luôn online

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buff2", buff2))
    app.add_handler(CommandHandler("huybuff2", huybuff2))
    app.add_handler(CommandHandler("adduser", adduser))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
