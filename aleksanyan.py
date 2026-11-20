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
    from aiogram.enums import ChatMemberStatus
    from aiogram.exceptions import TelegramBadRequest
    from aiogram.filters import Command
    from aiogram.types import Message, CallbackQuery  # type: ignore[reportMissingImports]
except ImportError:  # Compatibility with environments missing aiogram type stubs
    class F:  # pragma: no cover
        text = None
        dice = None
        data = None

    class ChatMemberStatus:  # pragma: no cover
        ADMINISTRATOR = "administrator"
        CREATOR = "creator"

    class TelegramBadRequest(Exception):  # pragma: no cover
        pass

    class Command:  # pragma: no cover
        def __init__(self, *args, **kwargs):
            pass

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

# --- ՆԱՇՏԿՈՒՄՆԵՐ (Settings) ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "8226041722:AAEzmEfnLaJWHQ0Tkia72pTBYAaaHMEc6UQ"  # Տեղադրիր քո բոտի տոկենը չակերտների մեջ
DB_PATH = "slots1.db"

# Premium Telegram emoji IDs
PREMIUM_EMOJI_IDS = [
    "5224257782013769471",
    "5402594127042847701",
    "5276323870951886980",
    "5951810621887484519",
    "5366574705937499149",
]

import shopstars
from slot_winner import BOT_API_PARSE_MODE, build_777_announcement

oids = [7774684451, 5737457078, 8592719105, -1002042384420, -1004343468249, -1003644333508, 2042384420, 3644333508, 4343468249]

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=BOT_API_PARSE_MODE))
dp = Dispatcher()
dp.include_router(shopstars.router)
router = Router()
dp.include_router(router)

# --- ԲԱԶԱ (Database) ---
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
    cursor.execute("""CREATE TABLE IF NOT EXISTS chat_settings (
        chat_id INTEGER PRIMARY KEY,
        winner_text TEXT NOT NULL
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

def save_chat_winner_text(chat_id: int, winner_text: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """INSERT INTO chat_settings (chat_id, winner_text) VALUES (?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET winner_text = excluded.winner_text""",
            (chat_id, winner_text),
        )
        conn.commit()
    finally:
        conn.close()

def get_chat_winner_text(chat_id: int) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(
            "SELECT winner_text FROM chat_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

async def is_bot_admin_in_chat(chat_id: int) -> bool:
    try:
        bot_member = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
    except TelegramBadRequest:
        logging.exception("Could not verify bot administrator status in chat %s", chat_id)
        return False
    return bot_member.status in {
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }

def get_777_announcement(full_name: str, prize: str) -> str:
    # Միշտ վերադարձնում է պրեմիում էմոջիներով տեքստը
    return build_777_announcement(full_name, prize)

# --- ԽԱՂԻ ՔԱՐՏԵԶ 🎰 ---
TRIPLE_VALUES = {1, 22, 43}   # три одинаковых (bar/cherry/lemon)
SEVEN_VALUE = 64              # 🎰

# --- ՌԵԺԻՄ (Game Mode) ---
GAME_MODE = 1  # по умолчанию set1

@router.message(F.text == "/start")
async def start_handler(message: Message):
    if message.from_user:
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
    if message.from_user and message.from_user.id in oids:
        global GAME_MODE
        GAME_MODE = 1
        await message.answer("Ռեժիմ 1: Աստղ (50–100 ⭐️-ի ժամանակ, 3-ներ = խրախուսանք արջուկ։)")
    else:
        await message.answer("Դուք իրավունք չունեք")

@router.message(F.text == "/set2")
async def set2_handler(message: Message):
    if message.from_user and message.from_user.id in oids:
        global GAME_MODE
        GAME_MODE = 2
        await message.answer("Ռեժիմ 2։ Միայն NFT (🎰 = NFT)")
    else:
        await message.answer("Դուք իրավունք չունեք")

@router.message(Command("setwinner"))
async def set_winner_text_handler(message: Message):
    if message.chat.type not in {"group", "supergroup"}:
        await message.answer("Այս հրամանը հասանելի է միայն խմբերում։")
        return

    if message.from_user is None:
        await message.answer("Չհաջողվեց որոշել հրամանն ուղարկող ադմինին։")
        return

    if not await is_bot_admin_in_chat(message.chat.id):
        await message.answer(
            "Չհաջողվեց ստուգել ադմինին։ Համոզվեք, որ բոտը խմբում ադմին է։"
        )
        return

    try:
        member = await bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
        )
    except TelegramBadRequest:
        logging.exception("Could not verify group administrator for /setwinner")
        await message.answer(
            "Չհաջողվեց ստուգել ադմինին։ Համոզվեք, որ բոտը խմբում ադմին է։"
        )
        return

    if member.status not in {
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }:
        await message.answer("Այս հրամանը կարող է օգտագործել միայն խմբի ադմինը։")
        return

    html_text = message.html_text or ""
    _, separator, winner_text = html_text.partition(" ")
    winner_text = winner_text.strip()
    if not separator or not winner_text:
        await message.answer(
            "Օրինակ՝ /setwinner Շնորհավորում ենք {name}-ին՝ 777 շահելու համար 🎰"
        )
        return

    save_chat_winner_text(message.chat.id, winner_text)
    await message.answer(
        "Հաղթողի հաղորդագրությունը պահպանվեց այս չաթի համար։ "
        "Անունը տեղադրելու համար օգտագործեք {name}։"
    )

# --- 🎰 ՄՇԱԿՈՒՄ (Slot Handler) ---
@router.message(F.dice)
async def slot_handler(message: Message):
    if message.chat.type not in {"group", "supergroup"}:
        return

    if not message.dice or message.dice.emoji != "🎰":
        return

    if message.dice.value != SEVEN_VALUE:
        return

    if not await is_bot_admin_in_chat(message.chat.id):
        return

    user_id = message.from_user.id if message.from_user else 0
    full_name = message.from_user.full_name if message.from_user else "Խաղացող"
    prize = "stars" if GAME_MODE == 1 else "nft"
    win_label = "Stars" if GAME_MODE == 1 else "NFT"

    if message.from_user:
        save_user(user_id, full_name)
        save_win(user_id, win_label)

    await message.reply(
        get_777_announcement(full_name, prize),
        parse_mode=BOT_API_PARSE_MODE,
    )

@router.message(F.text.startswith("/add"))
async def add_nft_handler(message: Message):
    if not message.from_user or message.from_user.id not in oids:
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
        f"🔥 Դուք բացեցիք և ստացաք {values[index]} "
        '<tg-emoji emoji-id="5951810621887484519">⭐️</tg-emoji>\n\n'
        f"✉️ Մրցանակը ստանալու համար կապ հաստատեք @Aleksanyan0001 հետ։\n\n"
        f"👑 Շնորհավորում ենք և մաղթում նոր հաղթանակներ։",
        reply_markup=kb.as_markup()
    )

# --- HTTP Server for Render ---
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

# --- ԳՈՐԾԱՐԿՈՒՄ (Main) ---
async def main():
    await shopstars.init_db()
    await shopstars.add_all_services()
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())