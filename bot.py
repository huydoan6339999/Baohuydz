from pyrogram import Client, filters
import requests
from keep_alive import keep_alive
import asyncio

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

# ID người dùng của bạn
OWNER_ID = 5736655322

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

# Kiểm tra người dùng có phải là bạn không
def is_owner(message):
    return message.from_user.id == OWNER_ID

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

# Lệnh /fl3 (Tăng follow tự động - chỉ bạn sử dụng)
@app.on_message(filters.command("fl3") & filters.group)
async def fl3_handler(client, message):
    if not is_owner(message):
        await message.reply_text("Bạn không có quyền sử dụng lệnh này!")
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "Vui lòng nhập username.\n"
            "Ví dụ: /fl3 nvp31012007"
        )
        return
    
    username = message.command[1].strip()

    # Gọi API để lấy thông tin tài khoản
    api_url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"
    data = get_api_response(api_url)

    if data:
        # Kiểm tra xem dữ liệu có chứa thông tin cần thiết không
        if "UID:" in data and "Nick Name:" in data:
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

            follow_hien_tai = follow_ban_dau  # Không thêm 500 nữa

            # Soạn tin nhắn gửi lại
            text = (
                f"Tăng follow thành công cho: @{username}\n\n"
                f"**Thông Tin Tài Khoản:**\n"
                f"UID: `{uid}`\n"
                f"Nick Name: {nickname}\n\n"
                f"FOLLOW BAN ĐẦU: {follow_ban_dau}\n"
                f"FOLLOW HIỆN TẠI: {follow_hien_tai}"
            )
            await message.reply_text(text)
        else:
            await message.reply_text("Dữ liệu trả về không hợp lệ hoặc tài khoản không tồn tại.")
    else:
        await message.reply_text("Không lấy được dữ liệu từ API.")

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
        "/fl3 username - Tăng follow ảo\n\n"
        "Ví dụ: `/fl3 nvp31012007`"
    )

# Tự động gọi lệnh /fl3 mỗi 15 phút
async def auto_buff():
    while True:
        # Tên người dùng
        username = "nvp31012007"  # Thay username của bạn
        # Gọi lệnh /fl3 tự động
        api_url = f"https://nvp310107.x10.mx/fltikfam.php?username={username}&key={API_KEY}"
        data = get_api_response(api_url)

        if data:
            if "UID:" in data and "Nick Name:" in data:
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

                follow_hien_tai = follow_ban_dau  # Không thêm 500 nữa

                text = (
                    f"Tăng follow thành công cho: @{username}\n\n"
                    f"**Thông Tin Tài Khoản:**\n"
                    f"UID: `{uid}`\n"
                    f"Nick Name: {nickname}\n\n"
                    f"FOLLOW BAN ĐẦU: {follow_ban_dau}\n"
                    f"FOLLOW HIỆN TẠI: {follow_hien_tai}"
                )
                # Gửi tin nhắn tự động đến admin hoặc nhóm cụ thể
                await app.send_message(-1002221629819, text)  # Gửi vào nhóm bạn muốn

        await asyncio.sleep(15 * 60)  # Chờ 15 phút trước khi chạy lại

# Chạy bot
if __name__ == "__main__":
    keep_alive()
    print("Bot đang khởi động...")
    app.loop.create_task(auto_buff())  # Bắt đầu chạy tác vụ tự động
    app.run()
