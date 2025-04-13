from flask import Flask, jsonify
from threading import Thread
import logging

# Cấu hình Flask
app = Flask(__name__)

# Thiết lập log cho Flask
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    """
    Trang chính của ứng dụng. Thông báo bot đang hoạt động.
    """
    app.logger.info('Truy cập trang chủ')
    return "Bot is alive!"

@app.route('/status')
def status():
    """
    Endpoint kiểm tra trạng thái của bot.
    """
    app.logger.info('Truy cập trạng thái bot')
    return jsonify({
        'status': 'Bot is running',
        'version': '1.0',
        'message': 'Everything is working fine!'
    })

def run():
    """
    Chạy Flask App trên cổng 8080.
    """
    try:
        app.run(host='0.0.0.0', port=8080, debug=True)
    except Exception as e:
        app.logger.error(f"Không thể khởi động server: {str(e)}")

def keep_alive():
    """
    Chạy Flask App trong một luồng riêng biệt để tránh bị block các tiến trình khác.
    """
    t = Thread(target=run)
    t.daemon = True  # Cho phép thread tự động dừng khi chương trình chính kết thúc
    t.start()

# Chạy keep_alive() khi bạn cần duy trì bot
if __name__ == '__main__':
    keep_alive()
