import aiohttp
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Kích hoạt event loop lồng nhau nếu cần thiết (sử dụng trong Jupyter)
nest_asyncio.apply()

BOT_TOKEN = "6367532329:AAFzGAqQZ_f4VQqX7VbwAoQ7iqbFO07Hzqk"  # Đảm bảo token là đúng và hợp lệ

async def send_like_request(idgame: str) -> str:
    urllike = f"https://dichvukey.site/likeff2.php?uid={idgame}"
    max_retries = 5

    async with aiohttp.ClientSession() as session:
        for attempt in range(max_retries):
            try:
                async with session.get(urllike, timeout=15) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if isinstance(data, dict) and "status" in data:
                        if data["status"] == 2:
                            return "⚠️ Bạn đã đạt giới hạn lượt like hôm nay, vui lòng thử lại sau."
                        return (
                            f"👤 Tên: {data.get('username', 'Không xác định')}\n"
                            f"🆔 UID: {data.get('uid', 'Không xác định')}\n"
                            f"🎚 Level: {data.get('level', 'Không xác định')}\n"
                            f"👍 Like trước: {data.get('likes_before', 'Không xác định')}\n"
                            f"✅ Like sau: {data.get('likes_after', 'Không xác định')}\n"
                            f"➕ Tổng cộng: {data.get('likes_given', 'Không xác định')} like"
                        )
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt == max_retries - 1:
                    return "Sever đang quá tải, vui lòng thử lại sau."
                await asyncio.sleep(5)

    return "Không thể xử lý yêu cầu."

# /like <uid>
async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập đúng cú pháp: /like <uid>")
        return
    uid = context.args[0]
    result = await send_like_request(uid)
    await update.message.reply_text(result)

# /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào mừng bạn đến bot buff like!\nDùng lệnh /like <uid> hoặc gửi UID trực tiếp.")

# Gửi UID trực tiếp
async def handle_uid_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if uid.isdigit():
        result = await send_like_request(uid)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("UID không hợp lệ. Vui lòng gửi số UID.")

# Chạy bot
async def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("like", like_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_uid_message))
    print("Bot đã chạy.")
    await app.run_polling()

# Khởi động bot với kiểm tra event loop
if __name__ == "__main__":
    # Kiểm tra nếu event loop đang chạy, tránh lỗi "Cannot close a running event loop"
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("Event loop đã chạy sẵn.")
        else:
            asyncio.run(start_bot())
    except RuntimeError as e:
        print(f"Lỗi: {e}")
