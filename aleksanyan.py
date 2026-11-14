import asyncio
from html import escape
import logging
import os
import random
import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

try:
    from aiogram import Bot, Dispatcher, F, Router
    from aiogram.types import Message, CallbackQuery  # type: ignore[reportMissingImports]
except ImportError:  # Compatibility with environments missing aiogram type stubs
    class F:  # pragma: no cover
        text = None
        dice = None
        data = None

    class Bot:  # pragma: no cover
        def __init__(self, *args, **kwargs):
            pass

    class Dispatcher:  # pragma: no cover
        def include_router(self, *args, **kwargs):
            return None

        async def start_polling(self, *args, **kwargs):
            raise RuntimeError("aiogram is required to run this bot")

    class Router:  # pragma: no cover
        def message(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class Message:  # pragma: no cover
        pass

    class CallbackQuery:  # pragma: no cover
        pass

try:
    from aiogram.client.default import DefaultBotProperties  # type: ignore[reportMissingImports]
except ImportError:  # Compatibility with older aiogram versions
    class DefaultBotProperties:  # pragma: no cover
        def __init__(self, **kwargs):
            self.kwargs = kwargs

try:
    from aiogram.utils.keyboard import InlineKeyboardBuilder  # type: ignore[reportMissingImports]
except ImportError:  # Compatibility with older aiogram versions
    if TYPE_CHECKING:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup  # type: ignore[reportMissingImports]
    else:
        try:
            from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup  # type: ignore[reportMissingImports]
        except ImportError:
            class InlineKeyboardButton:  # pragma: no cover
                def __init__(self, *args, **kwargs):
                    pass

            class InlineKeyboardMarkup:  # pragma: no cover
                def __init__(self, *args, **kwargs):
                    pass

                def row(self, *args, **kwargs):
                    return self

    class InlineKeyboardBuilder:
        def __init__(self):
            self._buttons = []
            self._row_sizes = []

        def button(self, text: str, callback_data: str | None = None):
            self._buttons.append((text, callback_data))
            return self

        def adjust(self, *sizes):
            self._row_sizes = sizes
            return self

        def as_markup(self):
            row_size = max(self._row_sizes) if self._row_sizes else 1
            markup = InlineKeyboardMarkup(row_width=row_size)
            current_row = []

            for text, callback_data in self._buttons:
                current_row.append(
                    InlineKeyboardButton(text=text, callback_data=callback_data)
                )
                if len(current_row) >= row_size:
                    markup.row(*current_row)
                    current_row = []

            if current_row:
                markup.row(*current_row)

            return markup

from aiohttp import web

# --- Настройки ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg"
DB_PATH = "slots1.db"

import shopstars

oids = [7774684451, 5737457078, 8592719105, -1002042384420, -1004343468249, -1003644333508, 2042384420, 3644333508, 4343468249]

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(shopstars.router)
router = Router()
dp.include_router(router)

# --- База данных ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        reg_date TEXT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS wins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        win_type TEXT,
        timestamp TEXT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS NFT_LIST (
        nft_number INTEGER PRIMARY KEY,
        nft TEXT,
        used INTEGER DEFAULT 0,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

def generate_win():
    roll = random.random()
    if roll <= 0.90:  # 90%
        return random.choice(range(50, 65, 5))   # 50, 55, 60
    elif roll <= 0.99:  # 9%
        return random.choice(range(60, 75, 5))   # 60, 65, 70
    elif roll <= 0.9900000005:  # 0.00000005%
        return random.choice(range(70, 85, 5))   # 70, 75, 80
    else:  # 0.00000000001%
        return random.choice(range(80, 105, 5))  # 80, 85, 90, 95, 100

def save_user(user_id: int, full_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, full_name, reg_date) VALUES (?, ?, ?)",
                   (user_id, full_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_win(user_id: int, win_type: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO wins (user_id, win_type, timestamp) VALUES (?, ?, ?)",
                   (user_id, win_type, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_nft(nft_number: int, nft: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO NFT_LIST (nft_number, nft, timestamp) VALUES (?, ?, ?)",
                   (nft_number, nft, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_available_nfts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nft_number, nft FROM NFT_LIST WHERE used = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_nft_used(nft_number: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE NFT_LIST SET used = 1 WHERE nft_number = ?", (nft_number,))
    conn.commit()
    conn.close()

# --- Карта значений 🎰 ---
TRIPLE_VALUES = {1, 22, 43}   # три одинаковых (bar/cherry/lemon)
SEVEN_VALUE = 64              # 🎰

# --- Глобальный режим ---
GAME_MODE = 1  # по умолчанию set1

@router.message(F.text == "/start")
async def start_handler(message: Message):
    save_user(message.from_user.id, message.from_user.full_name)
    await message.answer(
        "Բարի գալուստ։ Խաղը սկսելու համար ուղարկեք 🎰 emoji-ն։"
    )

@router.callback_query(F.data == "play_slots")
async def play_slots_handler(callback: CallbackQuery):
    await callback.message.answer(
        "🎰 Խաղալու համար ուղարկեք 🎰 emoji-ն։"
    )
    await callback.answer()

@router.message(F.text == "/set1")
async def set1_handler(message: Message):
    if message.from_user.id in oids:
        global GAME_MODE
        GAME_MODE = 1
        await message.answer("Ռեժիմ 1: Աստղ (50–100 ⭐️-ի ժամանակ, 3-ներ = խրախուսանք արջուկ։)")
    else:
        await message.answer("Դուք իրավունք չունեք")

@router.message(F.text == "/set2")
async def set2_handler(message: Message):
    if message.from_user.id in oids:
        global GAME_MODE
        GAME_MODE = 2
        await message.answer("Ռեժիմ 2։ Միայն NFT (🎰 = NFT)")
    else:
        await message.answer("Դուք իրավունք չունեք")

# --- 🎰 обработка ---
@router.message(F.dice)
async def slot_handler(message: Message):
    if message.dice.emoji != "🎰":
        return

    value = message.dice.value
    save_user(message.from_user.id, message.from_user.full_name)

    if GAME_MODE == 1:
        if value == SEVEN_VALUE:  # 🎰
            kb = InlineKeyboardBuilder()
            for i in range(12):
                kb.button(text="⭐️", callback_data=f"stars_{i}:{message.from_user.id}")
            kb.adjust(3, 3, 3, 3)

            save_win(message.from_user.id, "Stars")
            await message.reply(
                "🎆 ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
                "😃 Դուք ստացաք 🎰 և այժմ կարող եք ընտրել ⭐️ կոճակը՝ պարզելու ձեր հաղթած աստղերը:",
                reply_markup=kb.as_markup()
            )

        elif value in TRIPLE_VALUES:
            await message.reply(
                f"😔 Կներեք, {message.from_user.first_name}, ձեզ չընկավ 🎰։\n"
                f"🎁 Որպես մխիթարանք դուք ստացաք 🧸\n"
                f"✉️ Խնդրում ենք կապ հաստատել @Aleksanyan0001"
            )
    elif GAME_MODE == 2:
        if value == SEVEN_VALUE:  # 🎰 → NFT
            available_nfts = get_available_nfts()
            if not available_nfts:
                await message.answer("❌ NFT չկա.")
                return

            kb = InlineKeyboardBuilder()
            for nft_number, _ in available_nfts[:6]:
                kb.button(text="NFT", callback_data=f"nft_{nft_number}:{message.from_user.id}")
            kb.adjust(3, 3)
            save_win(message.from_user.id, "NFT")
            await message.reply(
                "🎆 ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
                "😃 Դուք ստացաք 🎰 և շահեցիք՝ NFT:\n"
                "🎁 Ընտրեք ձեր NFT մրցանակը։\n"
                "✉️ Մրցանակը ստանալու համար կապ հաստատեք @Aleksanyan0001 հետ։\n\n"
                "🔥 Շնորհավորում ենք և մաղթում նոր հաղթանակներ։",
                reply_markup=kb.as_markup()
            )
        elif value in TRIPLE_VALUES:
            return

@router.message(F.text.startswith("/add"))
async def add_nft_handler(message: Message):
    if message.from_user.id not in oids:
        await message.answer("Դուք իրավունք չունեք")
        return

    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            await message.answer("Օրինակը` /add <nft_number> <nft>")
            return

        nft_number = int(parts[1])
        nft_value = parts[2].strip()

        save_nft(nft_number, nft_value)
        await message.answer(f"NFT փոխվեց` #{nft_number} — {nft_value}")
    except Exception as e:
        await message.answer(f"⚠️ Խնդիր` {e}")

@router.callback_query(F.data.startswith("nft_"))
async def nft_callback(call: CallbackQuery):
    try:
        nft_data, winner_id = call.data.split(":")
        nft_number = int(nft_data.removeprefix("nft_"))
    except (AttributeError, ValueError):
        await call.answer("❗ Սխալ ընտրություն։", show_alert=True)
        return

    if str(call.from_user.id) != winner_id:
        await call.answer("⛔ Միայն հաղթողը!", show_alert=True)
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.execute(
            "SELECT nft FROM NFT_LIST WHERE nft_number = ? AND used = 0",
            (nft_number,)
        )
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            await call.answer("❗ Այս NFT-ն այլևս հասանելի չէ։", show_alert=True)
            return

        conn.execute(
            "UPDATE NFT_LIST SET used = 1 WHERE nft_number = ? AND used = 0",
            (nft_number,)
        )
        conn.commit()
    finally:
        conn.close()

    await call.message.edit_text(
        f"🎁 Ձեր NFT մրցանակը՝ {escape(row[0])}\n"
        "✉️ Հարցերի համար կապ հաստատեք @Aleksanyan0001 հետ։"
    )
    await call.answer()

@router.callback_query(F.data.startswith("stars_"))
async def stars_callback(call: CallbackQuery):
    data, winner_id = call.data.split(":")
    if str(call.from_user.id) != winner_id:
        await call.answer("⛔ Միայն հաղթողը!", show_alert=True)
        return

    index = int(data.split("_")[1])

    # генерируем числа для всех кнопок
    values = [generate_win() for _ in range(12)]

    kb = InlineKeyboardBuilder()
    for i, val in enumerate(values):
        if i == index:
            kb.button(text=f"✅ {val}", callback_data="disabled")
        else:
            kb.button(text=str(val), callback_data="disabled")
    kb.adjust(3, 3, 3, 3)

    await call.message.edit_text(
        f"🎆 ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ, {call.from_user.first_name}!\n\n"
        f"🔥 Դուք բացեցիք և ստացաք {values[index]} ⭐️\n\n"
        f"✉️ Մրցանակը ստանալու համար կապ հաստատեք @Aleksanyan0001 հետ։\n\n"
        f"👑 Շնորհավորում ենք և մաղթում նոր հաղթանակներ։",
        reply_markup=kb.as_markup()
    )

# --- HTTP Сервер для Render ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

# --- Запуск ---
async def main():
    await shopstars.init_db()
    await shopstars.add_all_services()
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
