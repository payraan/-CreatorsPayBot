from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DONATION_AMOUNTS, MIN_AMOUNTS

def get_start_keyboard(creator_slug: str = None):
    keyboard = [
        [InlineKeyboardButton(text="💸 حمایت مالی", callback_data="donate_start")],
    ]
    
    if creator_slug:
        keyboard.append([InlineKeyboardButton(text="🤝 همکاری تجاری (اسپانسر)", callback_data=f"sponsor_specific:{creator_slug}")])
    else:
        keyboard.append([InlineKeyboardButton(text="🤝 درخواست اسپانسرینگ", callback_data="sponsor_general")])

    keyboard.append([InlineKeyboardButton(text="👤 پروفایل من", callback_data="my_profile")])
    keyboard.append([InlineKeyboardButton(text="📞 پشتیبانی", url="https://t.me/Narmoon_support")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_amount_keyboard():
    buttons = []
    row = []
    for amount in DONATION_AMOUNTS:
        row.append(InlineKeyboardButton(text=f"{amount}$", callback_data=f"amount_{amount}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="✏️ مبلغ دلخواه", callback_data="amount_custom")])
    buttons.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_network_keyboard(amount: int):
    buttons = []
    if amount >= MIN_AMOUNTS["BSC"]:
        buttons.append([InlineKeyboardButton(text="🔸 BSC (BEP20) - کارمزد کم", callback_data="net_BSC")])
    if amount >= MIN_AMOUNTS["POLYGON"]:
        buttons.append([InlineKeyboardButton(text="🟣 Polygon - بدون کارمزد", callback_data="net_POLYGON")])
    if amount >= MIN_AMOUNTS["TRON"]:
        buttons.append([InlineKeyboardButton(text="🔺 TRON (TRC20)", callback_data="net_TRON")])
    buttons.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_amount")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_tx")]
    ])

def get_profile_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_start")]
    ])

def get_budget_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔻 زیر ۱۰۰ تتر", callback_data="budget_under_100")],
        [InlineKeyboardButton(text="🔹 ۱۰۰ تا ۵۰۰ تتر", callback_data="budget_100_500")],
        [InlineKeyboardButton(text="🔸 ۵۰۰ تا ۱۰۰۰ تتر", callback_data="budget_500_1000")],
        [InlineKeyboardButton(text="💎 بالای ۱۰۰۰ تتر", callback_data="budget_plus_1000")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_sponsor")]
    ])

def get_sponsor_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_sponsor")]
    ])
