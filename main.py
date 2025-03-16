import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import CommandHandler, Updater, JobQueue
import time

# Thông tin bot (Sử dụng token và chat_id của bạn)
TOKEN = "7438273610:AAEOwwV6k81kmLCpr88BS5yVAUSK0F59K7A"  # Token của bot Telegram
CHAT_ID = "5416288081"  # Chat ID của bạn
URL = "https://www.ur-net.go.jp/chintai/sp/kanto/saitama/result/?skcs=229&skcs=229&tdfk=11&todofuken=saitama"

# Khởi tạo bot Telegram
bot = Bot(token=TOKEN)

# Hàm kiểm tra nhà mới
def check_ur_housing():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = soup.find_all("div", class_="p-search-list-item__header")
    
    new_houses = []
    for listing in listings:
        title = listing.get_text(strip=True)
        new_houses.append(title)
    
    return new_houses

# Hàm gửi tin nhắn thông báo nhà mới
def send_alert(context):
    houses = check_ur_housing()
    if houses:
        message = "🏠 Danh sách nhà mới UR tại Wakōshi:\n\n" + "\n".join(houses)
        bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        bot.send_message(chat_id=CHAT_ID, text="Hiện tại không có nhà mới.")

# Hàm start bot
def start(update, context):
    update.message.reply_text("Chào bạn! Gõ /check để kiểm tra nhà mới.")

# Hàm main, chạy bot
def main():
    # Khởi tạo updater và dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue  # Tạo job queue cho việc tự động gửi tin nhắn

    # Thêm các handler
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check", send_alert))

    # Đặt job tự động kiểm tra nhà mới mỗi 10 phút (600 giây)
    job_queue.run_repeating(send_alert, interval=600, first=0)  # Interval 600 giây = 10 phút

    # Chạy bot
    updater.start_polling()

if __name__ == "__main__":
    main()