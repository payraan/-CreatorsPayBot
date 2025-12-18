import html
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.inline import (
    get_platform_keyboard,
    get_categories_keyboard,
    get_creators_list_keyboard,
    get_creator_profile_keyboard,
    get_start_keyboard
)

router = Router()

# ذخیره موقت فیلترها
catalog_filters = {}

@router.callback_query(F.data == "catalog_start")
async def catalog_start(callback: CallbackQuery):
    await callback.answer()
    
    text = """📋 <b>کاتالوگ کریتورها</b>

ابتدا پلتفرم مورد نظر را انتخاب کنید:"""
    
    await callback.message.edit_text(text, reply_markup=get_platform_keyboard(), parse_mode="HTML")

@router.callback_query(F.data.startswith("catalog_platform:"))
async def select_platform(callback: CallbackQuery):
    await callback.answer()
    
    platform = callback.data.split(":")[1]
    if platform == "ALL":
        platform = None
    
    # ذخیره فیلتر
    catalog_filters[callback.from_user.id] = {"platform": platform, "category": None}
    
    categories = await db.get_all_categories()
    
    platform_text = "همه پلتفرم‌ها" if not platform else ("یوتیوب" if platform == "YOUTUBE" else "اینستاگرام")
    
    text = f"""📂 <b>انتخاب دسته‌بندی</b>

📱 پلتفرم: <b>{platform_text}</b>

دسته‌بندی مورد نظر را انتخاب کنید:"""
    
    await callback.message.edit_text(text, reply_markup=get_categories_keyboard(categories, platform), parse_mode="HTML")

@router.callback_query(F.data.startswith("catalog_category:"))
async def select_category(callback: CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split(":")
    category = parts[1] if parts[1] != "ALL" else None
    platform = parts[2] if len(parts) > 2 and parts[2] != "ALL" else None
    
    # ذخیره فیلتر
    catalog_filters[callback.from_user.id] = {"platform": platform, "category": category, "page": 0}
    
    creators = await db.get_public_creators(platform=platform, category=category)
    
    if not creators:
        text = """😕 <b>کریتوری یافت نشد!</b>

در این دسته‌بندی هنوز کریتوری ثبت نشده.
لطفاً دسته‌بندی دیگری را انتخاب کنید."""
        await callback.message.edit_text(text, reply_markup=get_platform_keyboard(), parse_mode="HTML")
        return
    
    # ساخت متن
    cat_info = await db.get_category_by_slug(category) if category else None
    cat_text = f"{cat_info['emoji']} {cat_info['name']}" if cat_info else "همه دسته‌ها"
    platform_text = "همه" if not platform else ("🔴 یوتیوب" if platform == "YOUTUBE" else "📸 اینستاگرام")
    
    text = f"""📋 <b>لیست کریتورها</b>

📂 دسته: <b>{cat_text}</b>
📱 پلتفرم: <b>{platform_text}</b>
👥 تعداد: <b>{len(creators)}</b> نفر

روی هر کریتور کلیک کنید تا پروفایلش را ببینید:"""
    
    await callback.message.edit_text(text, reply_markup=get_creators_list_keyboard(creators), parse_mode="HTML")

@router.callback_query(F.data.startswith("catalog_page:"))
async def change_page(callback: CallbackQuery):
    await callback.answer()
    
    page = int(callback.data.split(":")[1])
    
    filters = catalog_filters.get(callback.from_user.id, {})
    platform = filters.get("platform")
    category = filters.get("category")
    
    creators = await db.get_public_creators(platform=platform, category=category)
    
    # آپدیت صفحه
    catalog_filters[callback.from_user.id]["page"] = page
    
    cat_info = await db.get_category_by_slug(category) if category else None
    cat_text = f"{cat_info['emoji']} {cat_info['name']}" if cat_info else "همه دسته‌ها"
    platform_text = "همه" if not platform else ("🔴 یوتیوب" if platform == "YOUTUBE" else "📸 اینستاگرام")
    
    text = f"""📋 <b>لیست کریتورها</b>

📂 دسته: <b>{cat_text}</b>
📱 پلتفرم: <b>{platform_text}</b>
👥 تعداد: <b>{len(creators)}</b> نفر

صفحه {page + 1}:"""
    
    await callback.message.edit_text(text, reply_markup=get_creators_list_keyboard(creators, page), parse_mode="HTML")

@router.callback_query(F.data.startswith("creator_profile:"))
async def show_creator_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    slug = callback.data.split(":")[1]
    creator = await db.get_creator_by_slug(slug)
    
    if not creator:
        await callback.answer("❌ کریتور یافت نشد!", show_alert=True)
        return
    
    # ذخیره slug برای دونیت/اسپانسر
    await state.update_data(creator_slug=slug)
    
    # آیکون پلتفرم
    platform_emoji = "🔴 یوتیوب" if creator['platform'] == 'YOUTUBE' else "📸 اینستاگرام"
    
    # فالوور
    followers = creator['followers_count'] or 0
    if followers >= 1000000:
        followers_text = f"{followers / 1000000:.1f}M"
    elif followers >= 1000:
        followers_text = f"{followers / 1000:.1f}K"
    else:
        followers_text = str(followers)
    
    # بازه قیمت
    min_price = creator['min_sponsor_price'] or 0
    max_price = creator['max_sponsor_price'] or 0
    if min_price and max_price:
        price_text = f"{min_price} - {max_price} تتر"
    elif min_price:
        price_text = f"از {min_price} تتر"
    else:
        price_text = "توافقی"
    
    # لینک پروفایل
    profile_link = creator['profile_link'] or "ثبت نشده"
    
    # توضیحات
    description = creator['description'] or "توضیحاتی ثبت نشده است."
    
    # دسته‌بندی
    category = creator['category'] or "عمومی"
    cat_info = await db.get_category_by_slug(category) if creator['category'] else None
    cat_text = f"{cat_info['emoji']} {cat_info['name']}" if cat_info else "📁 عمومی"
    
    text = f"""👤 <b>{html.escape(creator['name'])}</b>

📱 پلتفرم: <b>{platform_emoji}</b>
📂 دسته: <b>{cat_text}</b>
👥 فالوور: <b>{followers_text}</b>
💰 بازه قیمت: <b>{price_text}</b>
🔗 پروفایل: {html.escape(profile_link)}

📝 <b>درباره:</b>
{html.escape(description)}"""
    
    await callback.message.edit_text(text, reply_markup=get_creator_profile_keyboard(slug), parse_mode="HTML")

@router.callback_query(F.data == "catalog_back_list")
async def back_to_list(callback: CallbackQuery):
    await callback.answer()
    
    filters = catalog_filters.get(callback.from_user.id, {})
    platform = filters.get("platform")
    category = filters.get("category")
    page = filters.get("page", 0)
    
    creators = await db.get_public_creators(platform=platform, category=category)
    
    if not creators:
        await catalog_start(callback)
        return
    
    cat_info = await db.get_category_by_slug(category) if category else None
    cat_text = f"{cat_info['emoji']} {cat_info['name']}" if cat_info else "همه دسته‌ها"
    platform_text = "همه" if not platform else ("🔴 یوتیوب" if platform == "YOUTUBE" else "📸 اینستاگرام")
    
    text = f"""📋 <b>لیست کریتورها</b>

📂 دسته: <b>{cat_text}</b>
📱 پلتفرم: <b>{platform_text}</b>
👥 تعداد: <b>{len(creators)}</b> نفر"""
    
    await callback.message.edit_text(text, reply_markup=get_creators_list_keyboard(creators, page), parse_mode="HTML")

@router.callback_query(F.data.startswith("donate_creator:"))
async def donate_from_profile(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split(":")[1]
    await state.update_data(creator_slug=slug)
    
    # ری‌دایرکت به فلوی دونیت
    callback.data = "donate_start"
    from handlers.donation import donate_start
    await donate_start(callback, state)
