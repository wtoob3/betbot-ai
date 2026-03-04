import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ================= НАСТРОЙКИ =================

BOT_TOKEN = "8720942857:AAHfptkAnExjWiRFc1fB8QM6IVuB5LVqEX0"
CHANNEL_USERNAME = "@MaksimOrlovAnalyst"
PARTNER_LINK = "https://1wrlst.com/?p=5wky"
ADMIN_ID = 5535931481

MAIN_MENU_IMAGE = "https://pin.it/JU3tOu1cB"
REGISTER_IMAGE = "https://pin.it/6ogc1RTQG"

# ============================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ================= БАЗА =================

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'ru',
    vip INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    photo_id TEXT,
    status TEXT DEFAULT 'pending'
)
""")

conn.commit()

# ================= ПЕРЕВОДЫ =================

TEXTS = {
    "ru": {"menu":"🏆 Главное меню","register":"📝 Регистрация","vip":"💎 VIP доступ","support":"💬 Поддержка","deposit":"📸 Отправьте фото депозита","success":"✅ Скрин отправлен","no_vip":"❌ Нет VIP"},
    "en": {"menu":"🏆 Main Menu","register":"📝 Registration","vip":"💎 VIP Access","support":"💬 Support","deposit":"📸 Send deposit screenshot","success":"✅ Screenshot sent","no_vip":"❌ No VIP access"},
    "es": {"menu":"🏆 Menú principal","register":"📝 Registro","vip":"💎 Acceso VIP","support":"💬 Soporte","deposit":"📸 Enviar captura","success":"✅ Captura enviada","no_vip":"❌ Sin VIP"},
    "pt": {"menu":"🏆 Menu principal","register":"📝 Registro","vip":"💎 Acesso VIP","support":"💬 Suporte","deposit":"📸 Enviar captura","success":"✅ Enviado","no_vip":"❌ Sem VIP"},
    "br": {"menu":"🏆 Menu principal","register":"📝 Cadastro","vip":"💎 VIP","support":"💬 Suporte","deposit":"📸 Enviar print","success":"✅ Print enviado","no_vip":"❌ Sem VIP"},
    "ar": {"menu":"🏆 Menú principal","register":"📝 Registro","vip":"💎 VIP","support":"💬 Soporte","deposit":"📸 Enviar captura","success":"✅ Enviado","no_vip":"❌ Sin VIP"},
    "tr": {"menu":"🏆 Ana Menü","register":"📝 Kayıt","vip":"💎 VIP","support":"💬 Destek","deposit":"📸 Ekran görüntüsü gönder","success":"✅ Gönderildi","no_vip":"❌ VIP yok"},
    "az": {"menu":"🏆 Əsas menyu","register":"📝 Qeydiyyat","vip":"💎 VIP","support":"💬 Dəstək","deposit":"📸 Şəkil göndər","success":"✅ Göndərildi","no_vip":"❌ VIP yoxdur"},
    "hi": {"menu":"🏆 मुख्य मेनू","register":"📝 पंजीकरण","vip":"💎 VIP","support":"💬 सहायता","deposit":"📸 स्क्रीनशॉट भेजें","success":"✅ भेजा गया","no_vip":"❌ VIP नहीं"},
    "sa": {"menu":"🏆 القائمة الرئيسية","register":"📝 تسجيل","vip":"💎 VIP","support":"💬 دعم","deposit":"📸 أرسل صورة","success":"✅ تم الإرسال","no_vip":"❌ لا يوجد VIP"},
    "kr": {"menu":"🏆 메인 메뉴","register":"📝 등록","vip":"💎 VIP","support":"💬 지원","deposit":"📸 스크린샷 보내기","success":"✅ 전송됨","no_vip":"❌ VIP 없음"}
}

def get_text(user_id, key):
    cursor.execute("SELECT language FROM users WHERE telegram_id=?", (user_id,))
    row = cursor.fetchone()
    lang = row[0] if row else "ru"
    return TEXTS.get(lang, TEXTS["ru"]).get(key)

# ================= СОСТОЯНИЯ =================

class DepositState(StatesGroup):
    waiting_photo = State()

# ================= СТАРТ =================

@dp.message(F.text == "/start")
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton(text="🇵🇹 Português", callback_data="lang_pt")],
        [InlineKeyboardButton(text="🇧🇷 Brasileiro", callback_data="lang_br")],
        [InlineKeyboardButton(text="🇦🇷 Argentino", callback_data="lang_ar")],
        [InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton(text="🇦🇿 Azərbaycan", callback_data="lang_az")],
        [InlineKeyboardButton(text="🇮🇳 Hindi", callback_data="lang_hi")],
        [InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_sa")],
        [InlineKeyboardButton(text="🇰🇷 한국어", callback_data="lang_kr")]
    ])
    await message.answer("🌍 Choose language:", reply_markup=keyboard)

# ================= ВЫБОР ЯЗЫКА =================

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    cursor.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (user_id,))
    cursor.execute("UPDATE users SET language=? WHERE telegram_id=?", (lang, user_id))
    conn.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Subscribe", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton(text="✅ Check", callback_data="check_sub")]
    ])

    await callback.message.answer("Subscribe to channel 👇", reply_markup=keyboard)

# ================= ПРОВЕРКА ПОДПИСКИ =================

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if member.status in ["member", "administrator", "creator"]:
        await show_menu(callback.message, user_id)
    else:
        await callback.message.answer("❌ Not subscribed")

# ================= ГЛАВНОЕ МЕНЮ =================

async def show_menu(message, user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(user_id,"register"), callback_data="register")],
        [InlineKeyboardButton(text=get_text(user_id,"vip"), callback_data="vip_info")],
        [InlineKeyboardButton(text=get_text(user_id,"support"), callback_data="support")]
    ])

    await message.answer_photo(
        MAIN_MENU_IMAGE,
        caption=get_text(user_id,"menu"),
        reply_markup=keyboard
    )

# ================= РЕГИСТРАЦИЯ =================

@dp.callback_query(F.data == "register")
async def register(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Register", url=PARTNER_LINK)],
        [InlineKeyboardButton(text="📸 Send deposit screenshot", callback_data="deposit")]
    ])

    await callback.message.answer_photo(
        REGISTER_IMAGE,
        caption="1️⃣ Register\n2️⃣ Deposit\n3️⃣ Send screenshot",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "deposit")
async def deposit_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(get_text(callback.from_user.id,"deposit"))
    await state.set_state(DepositState.waiting_photo)

@dp.message(DepositState.waiting_photo)
async def save_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Send photo only")
        return

    photo_id = message.photo[-1].file_id
    user_id = message.from_user.id

    cursor.execute("INSERT INTO deposits (telegram_id, photo_id) VALUES (?,?)",
                   (user_id, photo_id))
    conn.commit()

    await message.answer(get_text(user_id,"success"))
    await state.clear()

# ================= VIP ИНФО =================

@dp.callback_query(F.data == "vip_info")
async def vip_info(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cursor.execute("SELECT vip FROM users WHERE telegram_id=?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] == 1:
        await callback.message.answer("💎 VIP ACTIVE")
    else:
        await callback.message.answer(get_text(user_id,"no_vip"))

# ================= СЕКРЕТНАЯ КОМАНДА =================

@dp.message(F.text.startswith("/admin3"))
async def admin_vip(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        target_id = int(message.text.split()[1])
        cursor.execute("UPDATE users SET vip=1 WHERE telegram_id=?", (target_id,))
        conn.commit()
        await bot.send_message(target_id,"🎉 VIP ACTIVATED")
        await message.answer("✅ VIP issued")
    except:
        await message.answer("Usage: /admin3 USER_ID")

# ================= ЗАПУСК =================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())