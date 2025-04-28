from pyrogram import Client, filters
import requests
from keep_alive import keep_alive

# Thông tin bot
BOT_TOKEN = "6374595640:AAFw8Lo4XMiz8JhDVhA8lYMk--wcFGmRBg4"
API_ID = 27657608
API_HASH = "3b6e52a3713b44ad5adaa2bcf579de66"

# Khởi tạo bot
app = Client(
    "my_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# API Key để gọi web
API_KEY = "30T42025VN"

# Các nhóm được phép hoạt động
ALLOWED_GROUPS = [-1002221629819, -1002334731264]

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

# Kiểm tra nếu message thuộc nhóm cho phép
def is_allowed_group(message):
    return message.chat.id in ALLOWED_GROUPS

# Lệnh /fl1
@app.on_message(filters.command("fl1") & filters.group)
async def fl1_handler(client, message):
    if not is_allowed_group(message):
        return
    
    if len(message.command) < 2:
        await message.reply_text("Vui lòng nhập username. Ví dụ: /fl1 nvp31012007")
        return
    username = message.command[1].strip()
    url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"
    result = get_api_response(url)
    if result:
        await message.reply_text(result)
    else:
        await message.reply_text("Không lấy được dữ liệu từ API.")

# Lệnh /fl2
@app.on_message(filters.command("fl2") & filters.group)
async def fl2_handler(client, message):
    if not is_allowed_group(message):
        return
    
    if len(message.command) < 2:
        await message.reply_text("Vui lòng nhập username. Ví dụ: /fl2 nvp31012007")
        return
    username = message.command[1].strip()
    url = f"https://nvp310107.x10.mx/fltik.php?username={username}&key={API_KEY}"
    result = get_api_response(url)
    if result:
        await message.reply_text(result)
    else:
        await message.reply_text("Không lấy được dữ liệu từ API.")

# Lệnh /buff (Tăng follow)
@app.on_message(filters.command("buff") & filters.group)
async def buff_handler(client, message):
    if not is_allowed_group(message):
        return
    
    if len(message.command) < 3:
        await message.reply_text(
            "Vui lòng nhập username và số follow cần tăng.\n"
            "Ví dụ: /buff nvp31012007 500"
        )
        return
    
    username = message.command[1].strip()
    try:
        follow_da_tang = int(message.command[2].strip())
    except ValueError:
        await message.reply_text("Số follow cần tăng phải là số!")
        return

    # Gọi API để lấy thông tin tài khoản
    api_url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"
    data = get_api_response(api_url)

    if data and "UID" in data and "Nick Name" in data:
        # Xử lý dữ liệu API trả về
        lines = data.splitlines()
        uid = ""
        nickname = ""
        follow_ban_dau = 0

        for line in lines:
            if line.startswith("UID:"):
                uid = line.split("UID:")[1].strip()
            elif line.startswith("Nick Name:"):
                nickname = line.split("Nick Name:")[1].strip()
            elif line.startswith("Follow:"):
                try:
                    follow_ban_dau = int(line.split("Follow:")[1].strip())
                except:
                    follow_ban_dau = 0

        follow_hien_tai = follow_ban_dau + follow_da_tang

        # Soạn tin nhắn gửi lại
        text = (
            f"Tăng follow thành công cho: @{username}\n\n"
            f"**Thông Tin Tài Khoản:**\n"
            f"UID: `{uid}`\n"
            f"Nick Name: {nickname}\n\n"
            f"FOLLOW BAN ĐẦU: {follow_ban_dau}\n"
            f"FOLLOW ĐÃ TĂNG: {follow_da_tang}\n"
            f"FOLLOW HIỆN TẠI: {follow_hien_tai}"
        )
        await message.reply_text(text)

    else:
        await message.reply_text("Không lấy được dữ liệu tài khoản hoặc username không tồn tại.")

# Lệnh /start và /help
@app.on_message(filters.command(["start", "help"]))
async def start_handler(client, message):
    if not is_allowed_group(message):
        return
    
    await message.reply_text(
        "**Xin chào!**\n"
        "Tôi hỗ trợ các lệnh sau:\n\n"
        "/fl1 username - Kiểm tra bằng API fam\n"
        "/fl2 username - Kiểm tra bằng API thường\n"
        "/buff username số_lượng - Tăng follow ảo\n\n"
        "Ví dụ: `/buff nvp31012007 500`"
    )

# Chạy bot
if __name__ == "__main__":
    keep_alive()
    print("Bot đang khởi động...")
    app.run()
