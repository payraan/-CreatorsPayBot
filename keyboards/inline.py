from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DONATION_AMOUNTS, MIN_AMOUNTS

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 حمایت مالی", callback_data="donate_start")],
        [InlineKeyboardButton(text="👤 پروفایل من", callback_data="my_profile")],
        [InlineKeyboardButton(text="📞 پشتیبانی", url="https://t.me/Narmoon_support")]
    ])

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
        buttons.append([InlineKeyboardButton(text="Polygon - بدون کارمزد", callback_data="net_POLYGON")])
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
