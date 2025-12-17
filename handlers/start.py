from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.inline import get_start_keyboard, get_profile_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await db.add_user(message.from_user.id, message.from_user.username)
    
    args = message.text.split()
    if len(args) > 1:
        slug = args[1]
        creator = await db.get_creator_by_slug(slug)
        if creator:
            await state.update_data(creator_slug=slug)
            
            text = f"""👋 سلام {message.from_user.first_name}!

به صفحه حمایت مالی از <b>{creator['name']}</b> خوش آمدید.

اینجا می‌تونی مستقیم، بدون واسطه و با کریپتو از تولیدکننده محتوای مورد علاقه‌ت حمایت کنی. ❤️

👇 یکی از گزینه‌ها رو انتخاب کن:"""
            await message.answer(text, reply_markup=get_start_keyboard(), parse_mode="HTML")
            return
    
    text = """👋 سلام!

به <b>CreatorPay</b> خوش آمدید.
برای حمایت از یوتیوبر مورد علاقه‌ات، از لینک اختصاصی اون استفاده کن."""
    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "my_profile")
async def my_profile(callback: CallbackQuery):
    await callback.answer()
    
    stats = await db.get_user_stats(callback.from_user.id)
    donations = await db.get_user_donations(callback.from_user.id)
    
    total_donations = stats['total_donations'] if stats else 0
    total_amount = float(stats['total_amount']) if stats else 0
    
    text = f"""👤 <b>پروفایل شما</b>

🆔 آیدی: <code>{callback.from_user.id}</code>
📊 تعداد دونیت‌ها: {total_donations}
💰 مجموع حمایت‌ها: {total_amount} USDT

"""
    
    if donations:
        text += "📜 <b>آخرین دونیت‌ها:</b>\n\n"
        for d in donations:
            status_emoji = "✅" if d['status'] == 'APPROVED' else "⏳" if d['status'] in ['PENDING_TXID', 'PENDING_REVIEW'] else "❌"
            text += f"{status_emoji} {d['amount_expected']} USDT به {d['creator_name']}\n"
    else:
        text += "📜 هنوز دونیتی انجام ندادی!"
    
    await callback.message.edit_text(text, reply_markup=get_profile_keyboard(), parse_mode="HTML")
