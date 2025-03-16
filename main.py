import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler
import logging

# Kích hoạt logging để theo dõi lỗi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình Token và Chat ID
TOKEN = "7438273610:AAEOwwV6k81kmLCpr88BS5yVAUSK0F59K7A"
CHAT_ID = "5416288081"

# Hàm lấy danh sách căn hộ từ UR Wakoshi
def check_ur_housing():
    URL = "https://www.ur-net.go.jp/chintai/sp/kanto/saitama/result/?skcs=229&skcs=229&tdfk=11&todofuken=saitama"
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.find_all("div", class_="p-search-list-item__header")  # Cập nhật selector nếu cần
    
    new_houses = []
    for listing in listings:
        title = listing.get_text(strip=True)
        new_houses.append(title)

    print(new_houses)  # In kết quả ra console để kiểm tra
    return new_houses

# Hàm kiểm tra số căn hộ trống
def check_vacant_rooms():
    # Địa chỉ URL của trang web
    URL = "https://www.ur-net.go.jp/chintai/sp/kanto/saitama/result/?skcs=229&skcs=229&tdfk=11&todofuken=saitama"
    
    # Gửi yêu cầu GET để tải trang web
    response = requests.get(URL)
    
    # Phân tích cú pháp HTML của trang web
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm phần tử chứa số căn hộ trống
    vacancy_section = soup.find("div", class_="conditionmodal_count rep_hit-row-count")
    
    if vacancy_section:
        # Tìm số căn hộ trống
        vacant_rooms = vacancy_section.find("strong")
        
        if vacant_rooms:
            return vacant_rooms.get_text(strip=True)
    
    return "Không tìm thấy thông tin căn hộ trống"

# Hàm gửi thông báo về căn hộ trống
async def send_alert(update: Update, context):
    houses = check_ur_housing()  # Lấy danh sách căn hộ trống
    vacant_rooms = check_vacant_rooms()  # Kiểm tra số căn trống
    if houses:
        message = f"🏠 Danh sách nhà mới UR tại Wakōshi:\n\n" + "\n".join(houses) + f"\n\nSố căn hộ trống: {vacant_rooms}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(f"Hiện tại không có nhà mới. {vacant_rooms}")

# Hàm gửi thông báo tự động qua JobQueue
async def send_alert_job(context):
    houses = check_ur_housing()  # Lấy danh sách căn hộ trống
    vacant_rooms = check_vacant_rooms()  # Kiểm tra số căn trống
    if houses:
        message = f"🏠 Danh sách nhà mới UR tại Wakōshi:\n\n" + "\n".join(houses) + f"\n\nSố căn hộ trống: {vacant_rooms}"
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"Hiện tại không có nhà mới. {vacant_rooms}")

# Cấu hình Application và các handler
def main():
    # Tạo ứng dụng với bot token
    application = Application.builder().token(TOKEN).build()

    # Thêm handler cho lệnh /check
    application.add_handler(CommandHandler("check", send_alert))

    # Tạo JobQueue để gửi thông báo tự động mỗi 10 phút
    application.job_queue.run_repeating(send_alert_job, interval=600, first=0)  # Interval 600 giây = 10 phút

    # Chạy bot
    application.run_polling()

if __name__ == '__main__':
    main()
