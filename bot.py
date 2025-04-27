from pyrogram import Client, filters
import requests

# Thay YOUR_BOT_TOKEN thành token bot thật của bạn
BOT_TOKEN = "6374595640:AAF7FI7joZJwNgyiRM-7l3FPHOdkf8Z5axo"

app = Client("my_bot", bot_token=BOT_TOKEN)

API_KEY = "30T42025VN"

def get_api_response(api_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(api_url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

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

@app.on_message(filters.command(["start", "help"]))
async def start_handler(client, message):
    await message.reply_text(
        "**Xin chào!**\n"
        "Tôi hỗ trợ các lệnh:\n"
        "/fl1 username - Kiểm tra bằng API fam\n"
        "/fl2 username - Kiểm tra bằng API thường\n\n"
        "Ví dụ: `/fl1 nvp31012007`"
    )

if __name__ == "__main__":
    print("Bot đang khởi động...")
    app.run()
