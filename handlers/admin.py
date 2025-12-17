from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMIN_ID, ADMIN_CHAT_ID
from database import db

router = Router()

def get_admin_keyboard(ref_code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تایید", callback_data=f"adm:approve:{ref_code}")],
        [InlineKeyboardButton(text="❌ رد", callback_data=f"adm:reject:{ref_code}")]
    ])

async def notify_admin(bot: Bot, user_id: int, username: str, creator_name: str, amount: float, network: str, ref_code: str, proof_type: str, proof_value: str):
    user_display = f"@{username}" if username else "بدون یوزرنیم"
    
    text = f"""🚨 تراکنش جدید نیاز به بررسی!

👤 کاربر: {user_display} (ID: {user_id})
🎬 برای: {creator_name}
💰 مبلغ: {amount} USDT
🌐 شبکه: {network}
🆔 کد پیگیری: {ref_code}

🧾 مدرک ارسال شده: {proof_type}"""

    if proof_type == "SCREENSHOT":
        await bot.send_photo(ADMIN_CHAT_ID, proof_value, caption=text, reply_markup=get_admin_keyboard(ref_code))
    else:
        text += f"\n{proof_value}"
        await bot.send_message(ADMIN_CHAT_ID, text, reply_markup=get_admin_keyboard(ref_code))

@router.callback_query(F.data.startswith("adm:approve:"))
async def approve_transaction(callback: CallbackQuery, bot: Bot):
    ref_code = callback.data.split(":")[2]
    
    await db.approve_transaction(ref_code)
    tx = await db.get_transaction_by_ref(ref_code)
    
    await bot.send_message(tx['telegram_id'], f"""✅ دونیت شما تایید شد!

🆔 کد پیگیری: {ref_code}
💰 مبلغ: {tx['amount_expected']} USDT

از حمایت شما متشکریم! ❤️""")
    
    await callback.answer("✅ تایید شد!")
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("adm:reject:"))
async def reject_transaction(callback: CallbackQuery, bot: Bot):
    ref_code = callback.data.split(":")[2]
    
    await db.reject_transaction(ref_code)
    tx = await db.get_transaction_by_ref(ref_code)
    
    await bot.send_message(tx['telegram_id'], f"""❌ تراکنش شما رد شد.

🆔 کد پیگیری: {ref_code}

لطفاً با پشتیبانی تماس بگیرید.""")
    
    await callback.answer("❌ رد شد!")
    await callback.message.edit_reply_markup(reply_markup=None)

@router.message(Command("check_debt"))
async def check_debt(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ استفاده: /check_debt [slug]\n\nمثال: /check_debt skillvid")
        return
    
    slug = args[1]
    debt_info = await db.get_creator_debt(slug)
    
    if not debt_info:
        await message.answer(f"❌ یوتیوبر با slug '{slug}' یافت نشد.")
        return
    
    total = float(debt_info['total_received']) if debt_info['total_received'] else 0
    rate = float(debt_info['commission_rate'])
    debt = total * (rate / 100)
    
    text = f"""📊 گزارش مالی: {debt_info['name']}

💰 کل دریافتی تایید شده: {total} USDT
📈 نرخ کمیسیون: {rate}%
💵 بدهی به پلتفرم: {debt:.2f} USDT

📅 تعداد تراکنش‌های تایید شده: {debt_info['approved_count']}"""
    
    await message.answer(text)

@router.message(Command("add_creator"))
async def add_creator(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("""📝 برای اضافه کردن یوتیوبر، این فرمت رو بفرست:

/newcreator
slug: نام_انگلیسی
name: نام نمایشی
wallet_bsc: آدرس BSC
wallet_polygon: آدرس Polygon
wallet_tron: آدرس Tron

مثال:
/newcreator
slug: skillvid
name: اسکیل وید
wallet_bsc: 0x123...
wallet_polygon: 0x456...
wallet_tron: TXyz...""")

@router.message(Command("newcreator"))
async def new_creator(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        lines = message.text.split('\n')[1:]
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().lower()] = value.strip()
        
        required = ['slug', 'name', 'wallet_bsc', 'wallet_polygon', 'wallet_tron']
        for field in required:
            if field not in data:
                await message.answer(f"❌ فیلد '{field}' وارد نشده.")
                return
        
        await db.add_creator(data['slug'], data['name'], data['wallet_bsc'], data['wallet_polygon'], data['wallet_tron'])
        
        await message.answer(f"""✅ یوتیوبر جدید اضافه شد!

🔗 لینک: t.me/CreatorsPayBot?start={data['slug']}
📛 نام: {data['name']}""")
    
    except Exception as e:
        await message.answer(f"❌ خطا: {str(e)}")

# --- بخش اسپانسرینگ ---
@router.callback_query(F.data.startswith("lead:approve:"))
async def approve_lead(callback: CallbackQuery, bot: Bot):
    lead_id = int(callback.data.split(":")[2])
    
    lead = await db.get_lead(lead_id)
    
    if lead['creator_tg_id']:
        text_creator = f"""🎉 <b>پیشنهاد همکاری جدید!</b>

یک برند تمایل به همکاری با شما دارد.

🏢 <b>برند:</b> {lead['sponsor_name']}
💰 <b>بودجه:</b> {lead['budget_range']}
📝 <b>توضیحات:</b> {lead['description']}

👇 برای هماهنگی و پذیرش، به پشتیبانی پیام دهید:
@Narmoon_support"""
        
        try:
            await bot.send_message(lead['creator_tg_id'], text_creator, parse_mode="HTML")
            await db.update_lead_status(lead_id, "SENT_TO_CREATOR")
            await callback.answer("✅ ارسال شد!")
            await callback.message.edit_text(f"{callback.message.text}\n\n✅ <b>تایید و برای {lead['creator_name']} ارسال شد.</b>", parse_mode="HTML")
        except Exception as e:
            await callback.answer(f"خطا در ارسال: {str(e)}", show_alert=True)
    else:
        await db.update_lead_status(lead_id, "APPROVED_GENERAL")
        await callback.answer("✅ تایید شد!")
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ <b>تایید شد (عمومی).</b>\nادمین دستی پیگیری کند.", parse_mode="HTML")

@router.callback_query(F.data.startswith("lead:reject:"))
async def reject_lead(callback: CallbackQuery):
    lead_id = int(callback.data.split(":")[2])
    await db.update_lead_status(lead_id, "REJECTED")
    await callback.answer("❌ رد شد!")
    await callback.message.edit_text(f"{callback.message.text}\n\n❌ <b>رد شد.</b>", parse_mode="HTML")
