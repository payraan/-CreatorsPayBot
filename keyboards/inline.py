from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DONATION_AMOUNTS, MIN_AMOUNTS

# --- منوی اصلی ---
def get_start_keyboard(creator_slug: str = None):
    keyboard = [
        [InlineKeyboardButton(text="💸 حمایت مالی", callback_data="donate_start")],
    ]
    
    if creator_slug:
        keyboard.append([InlineKeyboardButton(text="🤝 همکاری تجاری (اسپانسر)", callback_data=f"sponsor_specific:{creator_slug}")])
    else:
        keyboard.append([InlineKeyboardButton(text="📋 لیست کریتورها", callback_data="catalog_start")])
        keyboard.append([InlineKeyboardButton(text="🤝 درخواست اسپانسرینگ", callback_data="sponsor_general")])

    keyboard.append([InlineKeyboardButton(text="👤 پروفایل من", callback_data="my_profile")])
    keyboard.append([InlineKeyboardButton(text="📞 پشتیبانی", url="https://t.me/Narmoon_support")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- کاتالوگ: انتخاب پلتفرم ---
def get_platform_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 یوتیوب", callback_data="catalog_platform:YOUTUBE"),
            InlineKeyboardButton(text="📸 اینستاگرام", callback_data="catalog_platform:INSTAGRAM")
        ],
        [InlineKeyboardButton(text="🌐 همه پلتفرم‌ها", callback_data="catalog_platform:ALL")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_start")]
    ])

# --- کاتالوگ: انتخاب دسته‌بندی ---
def get_categories_keyboard(categories: list, platform: str = None):
    keyboard = []
    row = []
    
    for cat in categories:
        callback = f"catalog_category:{cat['slug']}"
        if platform:
            callback += f":{platform}"
        
        row.append(InlineKeyboardButton(text=f"{cat['emoji']} {cat['name']}", callback_data=callback))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="📋 همه دسته‌ها", callback_data=f"catalog_category:ALL:{platform or 'ALL'}")])
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="catalog_start")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- کاتالوگ: لیست کریتورها ---
def get_creators_list_keyboard(creators: list, page: int = 0, per_page: int = 5):
    keyboard = []
    
    start = page * per_page
    end = start + per_page
    page_creators = creators[start:end]
    
    for c in page_creators:
        platform_emoji = "🔴" if c['platform'] == 'YOUTUBE' else "📸"
        followers = c['followers_count'] or 0
        if followers >= 1000000:
            followers_text = f"{followers // 1000000}M"
        elif followers >= 1000:
            followers_text = f"{followers // 1000}K"
        else:
            followers_text = str(followers)
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{platform_emoji} {c['name']} ({followers_text})",
                callback_data=f"creator_profile:{c['slug']}"
            )
        ])
    
    # دکمه‌های صفحه‌بندی
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ قبلی", callback_data=f"catalog_page:{page-1}"))
    if end < len(creators):
        nav_buttons.append(InlineKeyboardButton(text="بعدی ▶️", callback_data=f"catalog_page:{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت", callback_data="catalog_start")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- پروفایل کریتور ---
def get_creator_profile_keyboard(slug: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤝 درخواست همکاری", callback_data=f"sponsor_specific:{slug}")],
        [InlineKeyboardButton(text="💸 حمایت مالی", callback_data=f"donate_creator:{slug}")],
        [InlineKeyboardButton(text="🔙 بازگشت به لیست", callback_data="catalog_back_list")]
    ])

# --- دونیت ---
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

# --- اسپانسرشیپ ---
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
