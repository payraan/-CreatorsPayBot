from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database import db

router = Router()

def get_admin_keyboard(ref_code: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تایید", callback_data=f"adm:approve:{ref_code}")],
        [InlineKeyboardButton(text="❌ رد", callback_data=f"adm:reject:{ref_code}")]
    ])

async def notify_admin(bot: Bot, user_id: int, username: str, creator_name: str, amount: float, network: str, ref_code: str, proof_type: str, proof_value: str):
    text = f"""🚨 **تراکنش جدید نیاز به بررسی!**

👤 کاربر: @{username} (ID: {user_id})
🎬 برای: {creator_name}
💰 مبلغ: {amount} USDT
🌐 شبکه: {network}
🆔 کد پیگیری: `{ref_code}`

🧾 **مدرک ارسال شده:** {proof_type}"""

    if proof_type == "SCREENSHOT":
        await bot.send_photo(ADMIN_ID, proof_value, caption=text, reply_markup=get_admin_keyboard(ref_code), parse_mode="Markdown")
    else:
        text += f"\n`{proof_value}`"
        await bot.send_message(ADMIN_ID, text, reply_markup=get_admin_keyboard(ref_code), parse_mode="Markdown")

@router.callback_query(F.data.startswith("adm:approve:"))
async def approve_transaction(callback: CallbackQuery, bot: Bot):
    ref_code = callback.data.split(":")[2]
    
    # آپدیت دیتابیس
    await db.approve_transaction(ref_code)
    
    # گرفتن اطلاعات تراکنش
    tx = await db.get_transaction_by_ref(ref_code)
    
    # اطلاع به کاربر
    await bot.send_message(tx['telegram_id'], f"""✅ **دونیت شما تایید شد!**

🆔 کد پیگیری: `{ref_code}`
💰 مبلغ: {tx['amount_expected']} USDT

از حمایت شما متشکریم! ❤️""", parse_mode="Markdown")
    
    await callback.answer("✅ تایید شد!")
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("adm:reject:"))
async def reject_transaction(callback: CallbackQuery, bot: Bot):
    ref_code = callback.data.split(":")[2]
    
    # آپدیت دیتابیس
    await db.reject_transaction(ref_code)
    
    # گرفتن اطلاعات تراکنش
    tx = await db.get_transaction_by_ref(ref_code)
    
    # اطلاع به کاربر
    await bot.send_message(tx['telegram_id'], f"""❌ **تراکنش شما رد شد.**

🆔 کد پیگیری: `{ref_code}`

لطفاً با پشتیبانی تماس بگیرید.""", parse_mode="Markdown")
    
    await callback.answer("❌ رد شد!")
    await callback.message.edit_reply_markup(reply_markup=None)
