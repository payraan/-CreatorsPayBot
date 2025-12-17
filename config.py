from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# حداقل مبلغ برای هر شبکه (دلار)
MIN_AMOUNTS = {
    "BSC": 2,
    "POLYGON": 1,
    "TRON": 20
}

# مبالغ پیشنهادی دونیت
DONATION_AMOUNTS = [2, 5, 10, 20, 50, 100]

# آیدی عددی ادمین
ADMIN_ID = 1951665139
