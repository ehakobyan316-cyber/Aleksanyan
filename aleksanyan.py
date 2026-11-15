import asyncio
from html import escape
import logging
import os
import random
import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

try:
    from aiogram import Bot, Dispatcher, F, Router  # type: ignore[reportMissingImports]
    from aiogram.types import Message, CallbackQuery  # type: ignore[reportMissingImports]
except ImportError:
    class F:
        text = None
        dice = None
        data = None

    class Bot:
        def __init__(self, *args, **kwargs):
            pass

    class Dispatcher:
        def include_router(self, *args, **kwargs):
            return None

        async def start_polling(self, *args, **kwargs):
            raise RuntimeError("aiogram is required to run this bot")

    class Router:
        def message(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class Message:
        pass

    class CallbackQuery:
        pass

try:
    from aiogram.client.default import DefaultBotProperties  # type: ignore[reportMissingImports]
except ImportError:
    class DefaultBotProperties:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

try:
    from aiogram.utils.keyboard import InlineKeyboardBuilder  # type: ignore[reportMissingImports]
except ImportError:
    if TYPE_CHECKING:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    else:
        try:
            from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        except ImportError:
            class InlineKeyboardButton:
                def __init__(self, *args, **kwargs):
                    pass

            class InlineKeyboardMarkup:
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
import shopstars

# --- ՆԱՇՏԿՈՒՄՆԵՐ (Settings) ---
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg")
DB_PATH = "slots1.db"
PREMIUM_STAR_EMOJI_ID = "5951810621887484519"

oids = [7774684451, 5737457078, 8592719105, -1002042384420, -1004343468249, -1003644333508, 2042384420, 3644333508, 4343468249]

router = Router(name="slots_router")

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

# --- ԽԱՂԻ ՔԱՐՏԵԶ 🎰 ---
TRIPLE_VALUES = {1, 22, 43}   # три одинаковых (bar/cherry/lemon)
SEVEN_VALUE = 64              # 🎰

# --- ՌԵԺԻՄ (Game Mode) ---
GAME_MODE = 1  # по умолчанию set1

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

# --- 🎰 ՄՇԱԿՈՒՄ (Slot Handler) ---
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
