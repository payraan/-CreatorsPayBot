from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import SponsorshipFlow
from database import db
from config import ADMIN_CHAT_ID
from keyboards.inline import get_budget_keyboard, get_start_keyboard, get_sponsor_cancel_keyboard

router = Router()

@router.callback_query(F.data.startswith("sponsor_"))
async def start_sponsorship(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    creator_slug = None
    if "specific" in callback.data:
        creator_slug = callback.data.split(":")[1]
        await state.update_data(target_slug=creator_slug)
    
    await state.set_state(SponsorshipFlow.sponsor_name)
    
    text = "🏢 <b>خوش آمدید!</b>\n\nبرای شروع همکاری، لطفاً <b>نام برند یا شرکت</b> خود را بنویسید:"
    if creator_slug:
        creator = await db.get_creator_by_slug(creator_slug)
        if creator:
            text = f"🏢 <b>درخواست همکاری با {creator['name']}</b>\n\nلطفاً <b>نام برند یا شرکت</b> خود را بنویسید:"
        
    await callback.message.edit_text(text, reply_markup=get_sponsor_cancel_keyboard(), parse_mode="HTML")

@router.message(SponsorshipFlow.sponsor_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(SponsorshipFlow.contact_info)
    await message.answer("📞 لطفاً <b>شماره تماس</b> یا <b>آیدی تلگرام</b> خود را جهت هماهنگی ارسال کنید:", reply_markup=get_sponsor_cancel_keyboard(), parse_mode="HTML")

@router.message(SponsorshipFlow.contact_info)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(SponsorshipFlow.budget)
    await message.answer("💰 <b>بودجه تقریبی</b> شما برای این کمپین چقدر است؟", reply_markup=get_budget_keyboard(), parse_mode="HTML")

@router.callback_query(SponsorshipFlow.budget, F.data.startswith("budget_"))
async def get_budget(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    budget_map = {
        "budget_under_100": "زیر ۱۰۰ تتر",
        "budget_100_500": "۱۰۰ تا ۵۰۰ تتر",
        "budget_500_1000": "۵۰۰ تا ۱۰۰۰ تتر",
        "budget_plus_1000": "بالای ۱۰۰۰ تتر"
    }
    budget_text = budget_map.get(callback.data, "نامشخص")
    
    await state.update_data(budget=budget_text)
    await state.set_state(SponsorshipFlow.description)
    
    await callback.message.edit_text(f"💰 بودجه انتخاب شد: <b>{budget_text}</b>\n\n📝 لطفاً توضیحات کوتاهی درباره محصول یا سرویس خود بنویسید:", reply_markup=get_sponsor_cancel_keyboard(), parse_mode="HTML")

@router.message(SponsorshipFlow.description)
async def finish_sponsorship(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    creator_id = None
    target_slug = data.get("target_slug")
    if target_slug:
        creator = await db.get_creator_by_slug(target_slug)
        if creator:
            creator_id = creator['id']

    lead_id = await db.add_lead(
        sponsor_name=data.get("name"),
        contact=data.get("contact"),
        budget=data.get("budget"),
        desc=message.text,
        sponsor_tg_id=message.from_user.id,
        creator_id=creator_id
    )
    
    await message.answer("✅ <b>درخواست شما ثبت شد!</b>\n\nتیم ما به زودی درخواست را بررسی و با شما تماس می‌گیرد.", reply_markup=get_start_keyboard(target_slug), parse_mode="HTML")
    await state.clear()
    
    target_text = f"یوتیوبر: {target_slug}" if target_slug else "کمپین عمومی"
    
    admin_text = f"""🚨 <b>درخواست اسپانسرینگ جدید (#{lead_id})</b>

🏢 <b>برند:</b> {data.get('name')}
💰 <b>بودجه:</b> {data.get('budget')}
📞 <b>تماس:</b> {data.get('contact')}
👤 <b>اسپانسر:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>
🎯 <b>هدف:</b> {target_text}

📝 <b>توضیحات:</b>
{message.text}"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تایید و ارسال به یوتیوبر", callback_data=f"lead:approve:{lead_id}")],
        [InlineKeyboardButton(text="❌ رد درخواست", callback_data=f"lead:reject:{lead_id}")]
    ])
    
    await bot.send_message(ADMIN_CHAT_ID, admin_text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "cancel_sponsor")
async def cancel_sponsor(callback: CallbackQuery, state: FSMContext):
    await callback.answer("❌ انصراف داده شد.")
    await state.clear()
    await callback.message.edit_text("❌ عملیات لغو شد.\n\nبرای شروع مجدد /start را بزنید.")
