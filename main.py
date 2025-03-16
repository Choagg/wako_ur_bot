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
import requests
from bs4 import BeautifulSoup

def check_vacant_rooms():
    # Địa chỉ URL của trang web
    URL = "https://www.ur-net.go.jp/chintai/sp/kanto/saitama/result/?skcs=229&skcs=229&tdfk=11&todofuken=saitama"
    
    # Gửi yêu cầu GET để tải trang web
    response = requests.get(URL)
    
    # Phân tích cú pháp HTML của trang web
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm phần tử chứa số căn hộ trống
    vacancy_section = soup.find("dl", class_="cassettes_property_vacancy module_boxsvertical_blue")
    
    if vacancy_section:
        # Tìm số căn hộ trống
        vacant_rooms = vacancy_section.find("strong", class_="rep_bukken-count-room")
        
        if vacant_rooms:
            return vacant_rooms.get_text(strip=True)
    
    return "Không tìm thấy thông tin căn hộ trống"
import requests
from bs4 import BeautifulSoup

# URL của trang web bạn muốn lấy thông tin
URL = "https://www.ur-net.go.jp/chintai/sp/kanto/saitama/result/?skcs=229&skcs=229&tdfk=11&todofuken=saitama"
      # Thay thế bằng URL chính xác của trang bạn muốn kiểm tra

def get_vacancy_count():
    response = requests.get(URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Kiểm tra toàn bộ HTML của trang để xem liệu có phần tử 'rep_bukken-count-room' không
        print(soup.prettify())  # In ra HTML trang web để bạn có thể kiểm tra

        vacancy_count = soup.find('strong', class_='rep_bukken-count-room')
        
        if vacancy_count:
            return vacancy_count.text.strip()
        else:
            return "Không tìm thấy thông tin phòng trống."
    else:
        return "Lỗi khi truy cập trang web."

# Kiểm tra hàm lấy số căn trống
print(get_vacancy_count())
# Kiểm tra số căn hộ trống và in ra kết quả
vacant_rooms = check_vacant_rooms()
print("Số căn hộ trống:", vacant_rooms)
# Hàm gửi thông báo về căn hộ trống
async def send_alert(update: Update, context):
    houses = check_ur_housing()  # Lấy danh sách căn hộ trống
    if houses:
        message = "🏠 Danh sách nhà mới UR tại Wakōshi:\n\n" + "\n".join(houses)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Hiện tại không có nhà mới.")

# Hàm gửi thông báo tự động qua JobQueue
async def send_alert_job(context):
    houses = check_ur_housing()
    if houses:
        message = "🏠 Danh sách nhà mới UR tại Wakōshi:\n\n" + "\n".join(houses)
        await context.bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text="Hiện tại không có nhà mới.")

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
