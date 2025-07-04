import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from keep_alive import keep_alive
import requests

rank_filter = {'ranks': []}
proxies = []

# ================= RANDOM TÊN NGƯỜI VIỆT =================
def random_name():
    name_prefix = [
        'Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Vũ', 'Võ', 'Đặng', 'Bùi',
        'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Mai', 'Trịnh', 'Đoàn', 'Phan', 'Tạ'
    ]

    name_suffix = [
        'Văn An', 'Văn Bình', 'Văn Cường', 'Văn Dũng', 'Văn Hùng', 'Văn Khoa', 'Văn Lâm',
        'Văn Minh', 'Văn Nam', 'Văn Phong', 'Văn Quang', 'Văn Sơn', 'Văn Tài', 'Văn Thành', 'Văn Thắng',
        'Thị Anh', 'Thị Bình', 'Thị Chi', 'Thị Duyên', 'Thị Hạnh', 'Thị Hoa', 'Thị Huyền',
        'Thị Lan', 'Thị Mai', 'Thị Ngọc', 'Thị Phương', 'Thị Thảo', 'Thị Thu', 'Thị Trang', 'Thị Yến',
        'Hải Đăng', 'Minh Khôi', 'Tuấn Kiệt', 'Hoàng Nam', 'Anh Tuấn', 'Thanh Tùng', 'Bảo Long', 'Quốc Huy'
    ]

    return f'{random.choice(name_prefix)} {random.choice(name_suffix)}'

# ================= RANDOM DỮ LIỆU =================
def random_time():
    random_seconds = random.randint(0, 30 * 24 * 60 * 60)
    time = datetime.now() - timedelta(seconds=random_seconds)
    return time.strftime('%H:%M:%S %d-%m-%Y')

def random_register_date():
    random_days = random.randint(1000, 3000)
    time = datetime.now() - timedelta(days=random_days)
    return time.strftime('%H:%M:%S %d-%m-%Y')

def random_level():
    return 30

def random_quan_huy():
    return random.randint(0, 100)

def random_tuong():
    return random.randint(30, 120)

def random_skin():
    return random.randint(50, 500)

def random_SS():
    return random.randint(0, 5)

def random_SSS():
    return random.randint(0, 3)

def random_account_status():
    return 'Acc Full'

def random_rank():
    ranks = ['K.Cương V', 'K.Cương IV', 'T.Anh V', 'Cao Thủ', 'Đại Cao Thủ', 'B.Kim I']
    return random.choice(ranks)

def random_username():
    return 'user' + str(random.randint(10000, 99999))

def random_password():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choices(chars, k=10))

# ================= CHECK GARENA =================
def check_garena_account(username, password, proxy=None):
    url = "https://account.garena.com/api/login"
    proxies_dict = None
    if proxy:
        proxies_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

    try:
        response = requests.post(url, data={
            "account": username,
            "password": password
        }, proxies=proxies_dict, timeout=10)

        if response.status_code == 200 and 'uid' in response.text:
            return True  # Acc live
        else:
            return False  # Acc die
    except Exception as e:
        print(f"Lỗi proxy hoặc request: {e}")
        return False

# ================= TẠO ACC THEO MẪU =================
def generate_account_status(account_line):
    try:
        user = random_username()
        password = random_password()

        account_info = (
            f'{user}:{password} | '
            f'Name: {random_name()} | Level: {random_level()} | Rank: {random_rank()} | '
            f'Quân Huy: {random_quan_huy()} | Lịch Sử Nạp: No | Sò: 0 | Quốc Gia: VN | '
            f'Đăng Nhập Lần Cuối: {random_time()} | Ngày Đăng Ký: {random_register_date()} | '
            f'Tướng: {random_tuong()} | Skin: {random_skin()} | Authen: No | SĐT: Yes | Email: No | '
            f'Tình Trạng Email: Chưa Xác Thực | CMND: Yes | FB: {random.choice(["Live", "No"])} | Ban: No | '
            f'SS: {random_SS()} | SSS: {random_SSS()} | Anime: 0 | Other: 0 | '
            f'Tình Trạng: {random_account_status()}'
        )

        return account_info

    except Exception as e:
        return f'Lỗi xử lý: {account_line}'

# ================= DELAY AUTO =================
async def delay():
    await asyncio.sleep(random.uniform(1.0, 2.0))

# ================= LỌC FILE =================
async def check_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document
        if not document.file_name.endswith('.txt'):
            await update.message.reply_text("Vui lòng gửi file định dạng .txt.")
            return

        await update.message.reply_text("Đang xử lý file, vui lòng chờ...")

        file_path = f'downloads/{document.file_name}'
        os.makedirs('downloads', exist_ok=True)

        file = await document.get_file()
        await file.download_to_drive(file_path)

        result = []
        with open(file_path, 'r', encoding='utf-8') as f:
            accounts = f.readlines()

        for account in accounts:
            account = account.strip()
            if account:
                account_info = generate_account_status(account)
                if rank_filter['ranks']:
                    for selected_rank in rank_filter['ranks']:
                        if f"Rank: {selected_rank}" in account_info:
                            result.append(account_info)
                            break
                else:
                    result.append(account_info)

        if not result:
            await update.message.reply_text("Không tìm thấy acc nào theo rank yêu cầu trong file!")
            os.remove(file_path)
            return

        result_file = f'downloads/checked_{document.file_name}'
        with open(result_file, 'w', encoding='utf-8') as f:
            for item in result:
                f.write(item + '\n\n')

        await update.message.reply_document(InputFile(result_file))
        await update.message.reply_text("Đã xử lý xong file!")

        os.remove(file_path)
        os.remove(result_file)

    except Exception as e:
        await update.message.reply_text(f"Lỗi xử lý file: {e}")

# ================= SET RANK =================
async def set_rank_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Vui lòng nhập danh sách rank cần lọc. Ví dụ: /filter Cao Thủ K.Cương V T.Anh V"
        )
        return

    selected_ranks = ' '.join(context.args).split()
    combined_ranks = []
    i = 0
    while i < len(selected_ranks):
        if selected_ranks[i] in ['K.Cương', 'T.Anh', 'B.Kim'] and i + 1 < len(selected_ranks):
            combined_ranks.append(f"{selected_ranks[i]} {selected_ranks[i + 1]}")
            i += 2
        else:
            combined_ranks.append(selected_ranks[i])
            i += 1

    valid_ranks = ['K.Cương V', 'K.Cương IV', 'T.Anh V', 'Cao Thủ', 'Đại Cao Thủ', 'B.Kim I']

    for rank in combined_ranks:
        if rank not in valid_ranks:
            await update.message.reply_text(f"Rank không hợp lệ: {rank}\nRank hợp lệ: {', '.join(valid_ranks)}")
            return

    rank_filter['ranks'] = combined_ranks
    await update.message.reply_text(f"Đã chọn lọc acc theo rank: {', '.join(combined_ranks)}\nBây giờ bạn có thể gửi file để bot lọc.")

# ================= ADD PROXY =================
async def add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng nhập proxy theo dạng ip:port hoặc user:pass@ip:port.")
        return

    proxy = context.args[0]
    proxies.append(proxy)
    await update.message.reply_text(f"Đã thêm proxy: {proxy}\nTổng số proxy hiện tại: {len(proxies)}")

# ================= CHECK GARENA LIVE =================
async def random_and_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    account = random.choice(accounts)
    if ':' in account:
        username, password = account.split(':', 1)
    else:
        await update.message.reply_text("Tài khoản không đúng định dạng user:pass.")
        return

    proxy = random.choice(proxies) if proxies else None
    is_live = check_garena_account(username, password, proxy)

    status = "✅ LIVE" if is_live else "❌ DIE"
    await update.message.reply_text(f"{account} → {status}")

    await delay()

# ================= BOT TELEGRAM =================
BOT_TOKEN = '6374595640:AAEdnPCVW05rcVjuHkx7RmjO_kRk2QbuCS4'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào bạn! Các lệnh hỗ trợ:\n"
        "/random - Random 1 tài khoản.\n"
        "/all - Gửi tất cả tài khoản.\n"
        "/allfile - Gửi file TXT chứa toàn bộ tài khoản.\n"
        "/filter rank1 rank2 ... - Chọn rank cần lọc.\n"
        "/addproxy proxy - Thêm proxy để sử dụng (không bắt buộc).\n"
        "/check - Random acc và kiểm tra live/die Garena.\n\n"
        "📂 Bạn cũng có thể gửi file .txt để lọc tự động."
    )

async def random_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    account = random.choice(accounts)
    account_info = generate_account_status(account)
    await update.message.reply_text(account_info)

async def all_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    await update.message.reply_text("Đang gửi toàn bộ tài khoản...")

    for account in accounts:
        account_info = generate_account_status(account)
        await update.message.reply_text(account_info)
        await asyncio.sleep(0.5)

async def all_accounts_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    result = []

    for account in accounts:
        account_info = generate_account_status(account)
        result.append(account_info)

    with open('acc_list.txt', 'w', encoding='utf-8') as file:
        for item in result:
            file.write(item + '\n\n')

    await update.message.reply_document(InputFile('acc_list.txt'))

# ================= READ ACCOUNTS =================
def read_accounts_from_file():
    accounts = []
    try:
        with open('input.txt', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    accounts.append(line)
        if not accounts:
            for i in range(5):
                accounts.append(f'user{i + 1}@example.com:password{i + 1}')
        return accounts
    except FileNotFoundError:
        with open('input.txt', 'w', encoding='utf-8') as file:
            for i in range(5):
                file.write(f'user{i + 1}@example.com:password{i + 1}\n')
        accounts = [f'user{i + 1}@example.com:password{i + 1}' for i in range(5)]
        return accounts

# ================= RUN BOT =================
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('random', random_account))
    app.add_handler(CommandHandler('all', all_accounts))
    app.add_handler(CommandHandler('allfile', all_accounts_file))
    app.add_handler(CommandHandler('filter', set_rank_filter))
    app.add_handler(CommandHandler('addproxy', add_proxy))
    app.add_handler(CommandHandler('check', random_and_check))
    app.add_handler(MessageHandler(filters.Document.ALL, check_file))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    keep_alive()
    run_bot()
