import asyncio
import logging
import os
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN", "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg")
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Բազայի ստեղծում և սխեմայի կարգավորում
def init_db():
    conn = sqlite3.connect("slots1.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 100
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Հիմնական մենյուի ստեղնաշար
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Խաղալ (Զառ)"), KeyboardButton(text="💰 Հաշվեկշիռ")],
            [KeyboardButton(text="📢 Ալիք AleksanyanFF Shop"), KeyboardButton(text="🛒 Ծառայություններ / Top-Up")]
        ],
        resize_keyboard=True
    )

# /start հրաման
@router.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    conn = sqlite3.connect("slots1.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?, ?)", (user_id, username, 100))
    conn.commit()
    conn.close()

    await message.answer(
        f"Բարև ձեզ, {message.from_user.first_name}! 👋\n\n"
        "ԲԱՑԱՌԻԿ ծառայություններ, խաղեր և արագ տոպ-ափներ **AleksanyanFF Shop**-ից։\n"
        "Ընտրեք անհրաժեշտ բաժինը ստորև բերված մենյուից 👇",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# Հաշվեկշռի ստուգում
@router.message(F.text == "💰 Հաշվեկշիռ")
async def balance_handler(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("slots1.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    balance = row[0] if row else 0
    await message.answer(f"💳 Ձեր ընթացիկ հաշվեկշիռը՝ **{balance} միավոր**", parse_mode="Markdown")

# Ալիքի կոճակ
@router.message(F.text == "📢 Ալիք AleksanyanFF Shop")
async def shop_channel_handler(message: Message):
    await message.answer(
        "📢 **AleksanyanFF Shop-ի պաշտոնական ալիքը:**\n\n"
        "Միացե՛ք մեր ալիքին՝ ամենավերջին նորությունների, զեղչերի և շահումների համար։\n"
        "🔗 Հղում՝ https://t.me/AleksanyanFFShop",
        parse_mode="Markdown"
    )

# Ծառայություններ / Top-Up
@router.message(F.text == "🛒 Ծառայություններ / Top-Up")
async def services_handler(message: Message):
    await message.answer(
        "🛒 **AleksanyanFF Shop - Ծառայություններ**\n\n"
        "• Free Fire Account Top-Up\n"
        "• Ակունդների գնում և վաճառք\n"
        "• Օպերատիվ աջակցություն և պատվերներ\n\n"
        "Պատվիրելու կամ հարցերի դեպքում գրեք ադմինիստրատորին։",
        parse_mode="Markdown"
    )

# Զառ խաղ
@router.message(F.text == "🎰 Խաղալ (Զառ)")
async def play_handler(message: Message):
    await message.answer_dice(emoji="🎰")

# Aiohttp վեբ սերվեր Render / Railway-ի համար
async def handle_ping(request):
    return web.Response(text="Bot is running and live!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")

# --- Գլխավոր գործարկման ֆունկցիա ---
async def main():
    try:
        # Մաքրում է հին կապերը Telegram-ից՝ conflict-ները բացառելու համար
        await bot.delete_webhook(drop_pending_updates=True)
        
        await asyncio.gather(
            web_server(),
            dp.start_polling(bot)
        )
    except Exception as e:
        logging.error(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(main())
