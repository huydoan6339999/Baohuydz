import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from keep_alive import keep_alive

rank_filter = {'ranks': []}

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


# ================= TẠO ACC THEO MẪU =================
def generate_account_status(account_line):
    try:
        if ':' in account_line:
            user, password = account_line.split(':', 1)
        else:
            user = account_line
            password = 'Không có mật khẩu'

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


# ================= BOT TELEGRAM =================
BOT_TOKEN = '6374595640:AAEdnPCVW05rcVjuHkx7RmjO_kRk2QbuCS4'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào bạn! Các lệnh hỗ trợ:\n"
        "/random - Random 1 tài khoản.\n"
        "/all - Gửi tất cả tài khoản.\n"
        "/allfile - Gửi file TXT chứa toàn bộ tài khoản.\n"
        "/filter rank1 rank2 ... - Chọn rank cần lọc.\n\n"
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


def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('random', random_account))
    app.add_handler(CommandHandler('all', all_accounts))
    app.add_handler(CommandHandler('allfile', all_accounts_file))
    app.add_handler(CommandHandler('filter', set_rank_filter))
    app.add_handler(MessageHandler(filters.Document.ALL, check_file))

    print("Bot đang chạy...")
    app.run_polling()


if __name__ == '__main__':
    keep_alive()
    run_bot()
