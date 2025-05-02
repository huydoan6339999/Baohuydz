import aiohttp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = '6374595640:AAHZm45pZN6QFx2UAdj4CcfA1KZ2ZC09Y7c'
ALLOWED_GROUP_ID = -1002221629819
ALLOWED_USER_IDS = [5736655322]
API_URL = 'https://api.thanhtien.site/lynk/dino/telefl.php'

buff2_tasks = {}

def is_allowed_user(user_id):
    return user_id in ALLOWED_USER_IDS

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào bạn! Tôi là bot hỗ trợ tăng follow TikTok.\n\n"
        "Lệnh sử dụng:\n"
        "/buff2 <username> - Treo buff follow\n"
        "/huybuff2 <username> - Hủy treo\n"
        "/listbuff2 - Danh sách đang treo\n"
        "/adduser <id> - Thêm người được phép\n"
        "/listuser - Danh sách người dùng được phép"
    )

# /buff2
async def buff2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        return await update.message.reply_text("Lệnh chỉ dùng trong nhóm được phép.")
    if not is_allowed_user(update.message.from_user.id):
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")
    if not context.args:
        return await update.message.reply_text("Vui lòng nhập username. Ví dụ: /buff2 username")

    username = context.args[0]
    if username in buff2_tasks:
        return await update.message.reply_text(f"Đã treo sẵn cho @{username}.")

    await update.message.reply_text(f"Đang treo tăng follow cho @{username} mỗi 15 phút.")

    async def auto_buff():
        while True:
            try:
                params = {
                    'user': username,
                    'userid': str(update.message.from_user.id),
                    'tokenbot': BOT_TOKEN
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL, params=params, timeout=20) as res:
                        data = await res.json()

                status_text = "✅ Thành công" if data.get('status', False) else "❌ Thất bại"
                reply_text = (
                    f"\n===== FOLLOW @{username} =====\n"
                    f"🏖️ Khu Vực: {data.get('khu_vuc', 'N/A')}\n"
                    f"👤 Tên: {data.get('name', 'N/A')}\n"
                    f"🆔 ID: {data.get('user_id', 'N/A')}\n"
                    f"📅 Ngày tạo: {data.get('create_time', 'N/A')}\n"
                    f"📌 Username: @{data.get('username', 'N/A')}\n"
                    f"👥 Trước: {data.get('followers_before', 0)} | Sau: {data.get('followers_after', 0)}\n"
                    f"✨ Đã thêm: {data.get('followers_add', 0)}\n"
                    f"💬 {data.get('message', '')}\n"
                    f"🔍 Trạng thái: {status_text}"
                )
                await update.message.reply_text(reply_text)
            except:
                pass
            await asyncio.sleep(900)

    task = asyncio.create_task(auto_buff())
    buff2_tasks[username] = task

# /huybuff2
async def huybuff2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ALLOWED_GROUP_ID:
        return await update.message.reply_text("Lệnh chỉ dùng trong nhóm được phép.")
    if not is_allowed_user(update.message.from_user.id):
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")
    if not context.args:
        return await update.message.reply_text("Vui lòng nhập username. Ví dụ: /huybuff2 username")

    username = context.args[0]
    if username in buff2_tasks:
        buff2_tasks[username].cancel()
        del buff2_tasks[username]
        await update.message.reply_text(f"Đã hủy treo follow cho @{username}.")
    else:
        await update.message.reply_text(f"Không có treo nào cho @{username}.")

# /listbuff2
async def listbuff2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update.message.from_user.id):
        return await update.message.reply_text("Bạn không có quyền.")
    if not buff2_tasks:
        return await update.message.reply_text("Không có username nào đang treo.")
    
    danh_sach = "\n".join(f"• @{u}" for u in buff2_tasks)
    await update.message.reply_text(f"Danh sách đang treo:\n{danh_sach}")

# /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update.message.from_user.id):
        return await update.message.reply_text("Bạn không có quyền thay đổi danh sách.")
    if not context.args:
        return await update.message.reply_text("Dùng: /adduser <ID>")

    try:
        new_id = int(context.args[0])
        if new_id in ALLOWED_USER_IDS:
            return await update.message.reply_text(f"ID {new_id} đã có trong danh sách.")
        ALLOWED_USER_IDS.append(new_id)
        await update.message.reply_text(f"Đã thêm ID {new_id} vào danh sách được phép.")
    except ValueError:
        await update.message.reply_text("ID không hợp lệ.")

# /listuser
async def listuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_user(update.message.from_user.id):
        return await update.message.reply_text("Bạn không có quyền.")
    danh_sach = "\n".join(f"• {uid}" for uid in ALLOWED_USER_IDS)
    await update.message.reply_text(f"Danh sách người dùng được phép:\n{danh_sach}")

# Main
def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buff2", buff2))
    app.add_handler(CommandHandler("huybuff2", huybuff2))
    app.add_handler(CommandHandler("listbuff2", listbuff2))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("listuser", listuser))
    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
