import random
import asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive

# ================= TÍNH UY TÍN =================
def calculate_trust_score(level, quan_huy, tuong, skin, banned, email_status, cmnd, fb_status):
    score = 0

    # Level cao: cộng 1 điểm mỗi level trên 25
    score += (level - 25)

    # Quân huy
    if quan_huy > 300:
        score += 5
    elif quan_huy > 100:
        score += 3

    # Tướng và Skin
    if tuong > 80:
        score += 5
    elif tuong > 50:
        score += 3

    if skin > 300:
        score += 5
    elif skin > 150:
        score += 3

    # Tình trạng tài khoản
    if banned == "No":
        score += 5
    if email_status == "Đã Xác Thực":
        score += 5
    if cmnd == "Yes":
        score += 3
    if fb_status == "Live":
        score += 3

    return score

# ================= RANDOM DỮ LIỆU =================
def random_name():
    first_names = ['Nguyen', 'Tran', 'Le', 'Pham', 'Hoang', 'Vu', 'Dang', 'Do']
    last_names = ['An', 'Bich', 'Cao', 'Duc', 'Hang', 'Kien', 'Mai', 'Tuan', 'Hien']
    return f'{random.choice(first_names)} {random.choice(last_names)}'

def random_level():
    return random.randint(25, 30)

def random_quan_huy():
    return random.randint(0, 400)

def random_SS():
    return random.randint(1, 30)

def random_SSS():
    return random.randint(0, 10)

def random_tuong():
    return random.randint(1, 120)

def random_skin():
    return random.randint(1, 500)

def random_account_status():
    statuses = ['acc full', 'acc trắng thông tin', 'acc trắng lỗi pass', 'acc dính mail']
    return random.choice(statuses)

def random_rank():
    ranks = ['K.Cương IV', 'T.Anh V', 'Chưa Có', 'Cao Thủ', 'Đại Cao Thủ', 'B.Kim I']
    return random.choice(ranks)

# ================= FILE TÀI KHOẢN =================
def read_accounts_from_file():
    accounts = []
    try:
        with open('input.txt', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and ':' in line:
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

# ================= TẠO ACC UY TÍN =================
def generate_account_status(account_line):
    try:
        if ':' in account_line:
            user, password = account_line.split(':', 1)
        else:
            user = account_line
            password = 'không có mật khẩu'

        level = random_level()
        quan_huy = random_quan_huy()
        tuong = random_tuong()
        skin = random_skin()
        banned = "No"
        email_status = random.choice(["Đã Xác Thực", "Chưa Xác Thực"])
        cmnd = "Yes"
        fb_status = "Live"

        trust_score = calculate_trust_score(level, quan_huy, tuong, skin, banned, email_status, cmnd, fb_status)

        account_info = (
            f'{user}:{password} | '
            f'Name: {random_name()} | Level: {level} | Rank: {random_rank()} | '
            f'Quân Huy: {quan_huy} | Lịch Sử Nạp: No | Sò: 0 | Quốc Gia: VN | '
            f'Đăng Nhập Lần Cuối: No | Ngày Đăng Ký: No | Tướng: {tuong} | Skin: {skin} | '
            f'Authen: No | SĐT: Yes | Email: No | Tình Trạng Email: {email_status} | '
            f'CMND: {cmnd} | FB: {fb_status} | Ban: {banned} | SS: {random_SS()} | SSS: {random_SSS()} | '
            f'Anime: No Skin | Other: No Skin | Tình Trạng: {random_account_status()} | '
            f'Uy Tín: {trust_score}/30'
        )

        return account_info, trust_score

    except Exception as e:
        return f'Lỗi xử lý: {account_line}', 0

# ================= BOT TELEGRAM =================
BOT_TOKEN = '6374595640:AAEdnPCVW05rcVjuHkx7RmjO_kRk2QbuCS4'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào bạn! Các lệnh hỗ trợ:\n"
        "/random - Random 1 tài khoản Uy Tín Cao.\n"
        "/all - Gửi tất cả tài khoản Uy Tín Cao.\n"
        "/allfile - Gửi file TXT chứa tất cả tài khoản Uy Tín Cao."
    )

async def random_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    random.shuffle(accounts)

    for account in accounts:
        account_info, trust_score = generate_account_status(account)
        if trust_score >= 15:
            await update.message.reply_text(account_info)
            return

    await update.message.reply_text("Không tìm thấy tài khoản Uy Tín Cao trong danh sách.")

async def all_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    count = 0

    await update.message.reply_text("Đang tìm tài khoản Uy Tín Cao...")

    for account in accounts:
        account_info, trust_score = generate_account_status(account)
        if trust_score >= 15:
            await update.message.reply_text(account_info)
            await asyncio.sleep(0.5)
            count += 1

    if count == 0:
        await update.message.reply_text("Không tìm thấy tài khoản Uy Tín Cao.")

async def all_accounts_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = read_accounts_from_file()
    result = []
    count = 0

    for account in accounts:
        account_info, trust_score = generate_account_status(account)
        if trust_score >= 15:
            result.append(account_info)
            count += 1

    if count == 0:
        await update.message.reply_text("Không tìm thấy tài khoản Uy Tín Cao.")
        return

    with open('uytin.txt', 'w', encoding='utf-8') as file:
        for item in result:
            file.write(item + '\n\n')

    await update.message.reply_document(InputFile('uytin.txt'))

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('random', random_account))
    app.add_handler(CommandHandler('all', all_accounts))
    app.add_handler(CommandHandler('allfile', all_accounts_file))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    keep_alive()
    run_bot()
