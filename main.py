import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Application, CommandHandler, CallbackContext, JobQueue
import logging

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
async def send_alert(context: CallbackContext):
    houses = check_ur_housing()
    if houses:
        message = "🏠 Danh sách nhà mới UR tại Wakōshi:\n\n" + "\n".join(houses)
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text="Hiện tại không có nhà mới.")

# Hàm start bot
async def start(update, context):
    await update.message.reply_text("Chào bạn! Gõ /check để kiểm tra nhà mới.")

# Hàm main, chạy bot
def main():
    # Khởi tạo Application mới (thay vì Updater)
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", send_alert))

    # Khởi tạo JobQueue để thực hiện công việc định kỳ
    job_queue = application.job_queue

    # Đặt job tự động kiểm tra nhà mới mỗi 10 phút (600 giây)
    job_queue.run_repeating(send_alert, interval=600, first=0)  # Interval 600 giây = 10 phút

    # Chạy bot
    application.run_polling()

if __name__ == "__main__":
    main()
