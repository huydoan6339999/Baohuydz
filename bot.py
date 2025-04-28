from pyrogram import Client, filters
import requests
from keep_alive import keep_alive

# Thông tin bot
BOT_TOKEN = "6374595640:AAFw8Lo4XMiz8JhDVhA8lYMk--wcFGmRBg4"
API_ID = 27657608  # <-- Bạn thay API_ID thật vào đây
API_HASH = "3b6e52a3713b44ad5adaa2bcf579de66"  # <-- Bạn thay API_HASH thật vào đây

# Khởi tạo bot
app = Client(
    "my_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# API Key để gọi web
API_KEY = "30T42025VN"

# Hàm gọi API
def get_api_response(api_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(api_url, headers=headers, timeout=30, verify=False)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

# Lệnh /fl1
@app.on_message(filters.command("fl1") & (filters.private | filters.group))
async def fl1_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("Vui lòng nhập username. Ví dụ: /fl1 nvp31012007")
        return
    username = message.command[1]
    url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"
    result = get_api_response(url)
    if result:
        await message.reply_text(result)
    else:
        await message.reply_text("Không lấy được dữ liệu từ API.")

# Lệnh /fl2
@app.on_message(filters.command("fl2") & (filters.private | filters.group))
async def fl2_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("Vui lòng nhập username. Ví dụ: /fl2 nvp31012007")
        return
    username = message.command[1]
    url = f"https://nvp310107.x10.mx/fltik.php?username={username}&key={API_KEY}"
    result = get_api_response(url)
    if result:
        await message.reply_text(result)
    else:
        await message.reply_text("Không lấy được dữ liệu từ API.")

# Lệnh /start và /help
@app.on_message(filters.command(["start", "help"]))
async def start_handler(client, message):
    await message.reply_text(
        "**Xin chào!**\n"
        "Tôi hỗ trợ các lệnh:\n"
        "/fl1 username - Kiểm tra bằng API fam\n"
        "/fl2 username - Kiểm tra bằng API thường\n\n"
        "Ví dụ: `/fl1 nvp31012007`"
    )

# Chạy bot
if __name__ == "__main__":
    keep_alive()
    print("Bot đang khởi động...")
    app.run()
