from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.inline import get_start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # ذخیره کاربر در دیتابیس
    await db.add_user(message.from_user.id, message.from_user.username)
    
    # چک کردن Deep Link
    args = message.text.split()
    if len(args) > 1:
        slug = args[1]
        creator = await db.get_creator_by_slug(slug)
        if creator:
            # ذخیره slug در state
            await state.update_data(creator_slug=slug)
            
            text = f"""👋 سلام {message.from_user.first_name}!

به صفحه حمایت مالی از **{creator['name']}** خوش آمدید.

اینجا می‌تونی مستقیم، بدون واسطه و با کریپتو از تولیدکننده محتوای مورد علاقه‌ت حمایت کنی. ❤️

👇 یکی از گزینه‌ها رو انتخاب کن:"""
            await message.answer(text, reply_markup=get_start_keyboard(), parse_mode="Markdown")
            return
    
    # بدون Deep Link
    text = """👋 سلام!

به **CreatorPay** خوش آمدید.
برای حمایت از یوتیوبر مورد علاقه‌ات، از لینک اختصاصی اون استفاده کن."""
    await message.answer(text, parse_mode="Markdown")
