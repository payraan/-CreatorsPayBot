from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import DonationFlow
from keyboards.inline import get_start_keyboard, get_amount_keyboard, get_network_keyboard, get_cancel_keyboard
from database import db
from services.utils import generate_ref_code
from handlers.admin import notify_admin

router = Router()

@router.callback_query(F.data == "donate_start")
async def donate_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DonationFlow.selecting_amount)
    
    text = """💎 **مبلغ حمایت را انتخاب کنید:**

چقدر دوست داری انرژی بدی؟
(مبالغ به تتر USDT هستند)"""
    
    await callback.message.edit_text(text, reply_markup=get_amount_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    
    text = """👋 سلام!

👇 یکی از گزینه‌ها رو انتخاب کن:"""
    
    await callback.message.edit_text(text, reply_markup=get_start_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "back_to_amount")
async def back_to_amount(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DonationFlow.selecting_amount)
    
    text = """💎 **مبلغ حمایت را انتخاب کنید:**

چقدر دوست داری انرژی بدی؟
(مبالغ به تتر USDT هستند)"""
    
    await callback.message.edit_text(text, reply_markup=get_amount_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("amount_"))
async def select_amount(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "amount_custom":
        await state.set_state(DonationFlow.custom_amount)
        await callback.message.edit_text("✏️ لطفاً مبلغ دلخواه را به عدد ارسال کنید (مثلاً: 15):")
        return
    
    amount = int(callback.data.split("_")[1])
    await state.update_data(amount=amount)
    await state.set_state(DonationFlow.selecting_network)
    
    text = f"""🌐 **انتخاب شبکه پرداخت:**

مبلغ: **{amount} USDT**

لطفاً شبکه‌ای که می‌خواهید با آن واریز کنید را انتخاب کنید.
⚠️ حتماً در کیف پول خودتان هم همین شبکه را انتخاب کنید."""
    
    await callback.message.edit_text(text, reply_markup=get_network_keyboard(amount), parse_mode="Markdown")

@router.message(DonationFlow.custom_amount)
async def custom_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount < 1:
            await message.answer("❌ مبلغ باید حداقل 1 دلار باشد.")
            return
    except ValueError:
        await message.answer("❌ لطفاً فقط عدد وارد کنید.")
        return
    
    await state.update_data(amount=amount)
    await state.set_state(DonationFlow.selecting_network)
    
    text = f"""🌐 **انتخاب شبکه پرداخت:**

مبلغ: **{amount} USDT**

لطفاً شبکه‌ای که می‌خواهید با آن واریز کنید را انتخاب کنید."""
    
    await message.answer(text, reply_markup=get_network_keyboard(amount), parse_mode="Markdown")

@router.callback_query(F.data.startswith("net_"))
async def select_network(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    network = callback.data.split("_")[1]
    data = await state.get_data()
    amount = data.get("amount")
    creator_slug = data.get("creator_slug", "skillvid")
    
    creator = await db.get_creator_by_slug(creator_slug)
    if not creator:
        await callback.message.edit_text("❌ خطا: یوتیوبر یافت نشد.")
        return
    
    wallet_key = f"wallet_{network.lower()}"
    wallet = creator[wallet_key]
    
    user_id = await db.get_user_id(callback.from_user.id)
    ref_code = generate_ref_code()
    
    await db.create_transaction(ref_code, user_id, creator['id'], amount, network)
    
    await state.update_data(ref_code=ref_code, network=network, creator_name=creator['name'])
    await state.set_state(DonationFlow.waiting_for_txid)
    
    text = f"""🧾 **فاکتور پرداخت**

🔸 **مبلغ:** {amount} USDT
🔸 **شبکه:** {network}
🆔 **کد پیگیری:** `{ref_code}`

👇 **آدرس کیف پول (کلیک کنید تا کپی شود):**
`{wallet}`

⚠️ **مراحل نهایی:**
۱. مبلغ را به آدرس بالا واریز کنید.
۲. **هش تراکنش (TXID)** یا **اسکرین‌شات رسید** را همینجا ارسال کنید.
۳. تا زمان تایید ادمین صبر کنید."""
    
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "cancel_tx")
async def cancel_transaction(callback: CallbackQuery, state: FSMContext):
    await callback.answer("❌ انصراف داده شد.")
    await state.clear()
    await callback.message.edit_text("❌ تراکنش لغو شد. برای شروع مجدد /start را بزنید.")

@router.message(DonationFlow.waiting_for_txid, F.photo)
async def receive_photo_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ref_code = data.get("ref_code")
    amount = data.get("amount")
    network = data.get("network")
    creator_name = data.get("creator_name")
    
    photo_id = message.photo[-1].file_id
    await db.update_transaction_proof(ref_code, "SCREENSHOT", photo_id)
    
    # اطلاع به ادمین
    await notify_admin(bot, message.from_user.id, message.from_user.username, creator_name, amount, network, ref_code, "SCREENSHOT", photo_id)
    
    await state.clear()
    await message.answer(f"""✅ **رسید شما دریافت شد!**

🆔 کد پیگیری: `{ref_code}`

لطفاً منتظر تایید ادمین باشید.
پس از تایید، پیام دریافت خواهید کرد.""", parse_mode="Markdown")

@router.message(DonationFlow.waiting_for_txid, F.text)
async def receive_text_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    ref_code = data.get("ref_code")
    amount = data.get("amount")
    network = data.get("network")
    creator_name = data.get("creator_name")
    
    await db.update_transaction_proof(ref_code, "TXID", message.text)
    
    # اطلاع به ادمین
    await notify_admin(bot, message.from_user.id, message.from_user.username, creator_name, amount, network, ref_code, "TXID", message.text)
    
    await state.clear()
    await message.answer(f"""✅ **هش تراکنش شما دریافت شد!**

🆔 کد پیگیری: `{ref_code}`

لطفاً منتظر تایید ادمین باشید.
پس از تایید، پیام دریافت خواهید کرد.""", parse_mode="Markdown")
