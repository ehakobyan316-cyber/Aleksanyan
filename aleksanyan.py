import asyncio
import logging
import os
import random
import sqlite3
from datetime import datetime
from html import escape

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

import shopstars


logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg"

DB_PATH = "slots1.db"
ADMIN_IDS = {
    7774684451,
    5737457078,
    8592719105,
    -1002042384420,
    -1004343468249,
    -1003644333508,
    2042384420,
    3644333508,
    4343468249,
}

MONEY = "<tg-emoji emoji-id='5224257782013769471'>💰</tg-emoji>"
MESSAGE = "<tg-emoji emoji-id='5402594127042847701'>💬</tg-emoji>"
HAPPY = "<tg-emoji emoji-id='5276323870951886980'>😃</tg-emoji>"
STAR = "<tg-emoji emoji-id='5951810621887484519'>⭐️</tg-emoji>"
GIFT = "<tg-emoji emoji-id='5366574705937499149'>🎁</tg-emoji>"
FIRE = "<tg-emoji emoji-id='5368324170671202286'>🔥</tg-emoji>"
DICE = "<tg-emoji emoji-id='5368361284419201529'>🎰</tg-emoji>"
CROWN = "<tg-emoji emoji-id='5217822164362739968'>👑</tg-emoji>"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()
dp.include_router(shopstars.router)
router = Router()
dp.include_router(router)

TRIPLE_VALUES = {1, 22, 43}
SEVEN_VALUE = 64
GAME_MODE = 1


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            reg_date TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS wins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            win_type TEXT,
            timestamp TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS NFT_LIST (
            nft_number INTEGER PRIMARY KEY,
            nft TEXT,
            used INTEGER DEFAULT 0,
            timestamp TEXT
        )""")


def generate_win() -> int:
    roll = random.random()
    if roll <= 0.90:
        return random.choice(range(50, 65, 5))
    if roll <= 0.99:
        return random.choice(range(60, 75, 5))
    if roll <= 0.9900000005:
        return random.choice(range(70, 85, 5))
    return random.choice(range(80, 105, 5))


def save_user(user_id: int, full_name: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, full_name, reg_date) VALUES (?, ?, ?)",
            (user_id, full_name, datetime.now().isoformat())
        )


def save_win(user_id: int, win_type: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO wins (user_id, win_type, timestamp) VALUES (?, ?, ?)",
            (user_id, win_type, datetime.now().isoformat())
        )


def save_nft(nft_number: int, nft: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO NFT_LIST (nft_number, nft, timestamp) VALUES (?, ?, ?)",
            (nft_number, nft, datetime.now().isoformat())
        )


def get_available_nfts() -> list[tuple[int, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT nft_number, nft FROM NFT_LIST WHERE used = 0"
        ).fetchall()


@router.callback_query(F.data == "play_slots")
async def play_slots_handler(callback: CallbackQuery) -> None:
    await callback.message.answer(
        f"{DICE} Խաղալու համար ուղարկեք 🎰 emoji-ն։"
    )
    await callback.answer()


@router.message(F.text == "/set1")
async def set1_handler(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Դուք իրավունք չունեք")
        return

    global GAME_MODE
    GAME_MODE = 1
    await message.answer(
        f"Ռեժիմ 1: Աստղ (50–100 {STAR}-ի ժամանակ, 3-ներ = խրախուսանք արջուկ։)"
    )


@router.message(F.text == "/set2")
async def set2_handler(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Դուք իրավունք չունեք")
        return

    global GAME_MODE
    GAME_MODE = 2
    await message.answer(f"Ռեժիմ 2։ Միայն NFT ({DICE} = NFT)")


@router.message(F.dice)
async def slot_handler(message: Message) -> None:
    if message.dice.emoji != "🎰":
        return

    value = message.dice.value
    save_user(message.from_user.id, message.from_user.full_name)

    if GAME_MODE == 1:
        if value == SEVEN_VALUE:
            keyboard = InlineKeyboardBuilder()
            for index in range(12):
                keyboard.button(
                    text="⭐️",
                    callback_data=f"stars_{index}:{message.from_user.id}"
                )
            keyboard.adjust(3, 3, 3, 3)
            save_win(message.from_user.id, "Stars")
            await message.reply(
                f"🎆 ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
                f"{HAPPY} Դուք ստացաք {DICE} և այժմ կարող եք ընտրել "
                f"{STAR} կոճակը՝ պարզելու ձեր հաղթած աստղերը:",
                reply_markup=keyboard.as_markup()
            )
        elif value in TRIPLE_VALUES:
            await message.reply(
                f"😔 Կներեք, {escape(message.from_user.first_name)}, "
                f"ձեզ չընկավ {DICE}։\n"
                f"{GIFT} Որպես մխիթարանք դուք ստացաք 🧸\n"
                f"{MESSAGE} Խնդրում ենք կապ հաստատել @Aleksanyan0001"
            )
        return

    if GAME_MODE == 2 and value == SEVEN_VALUE:
        available_nfts = get_available_nfts()
        if not available_nfts:
            await message.answer("❌ NFT չկա։")
            return

        keyboard = InlineKeyboardBuilder()
        for nft_number, _ in available_nfts[:6]:
            keyboard.button(
                text="NFT",
                callback_data=f"nft_{nft_number}:{message.from_user.id}"
            )
        keyboard.adjust(3, 3)
        save_win(message.from_user.id, "NFT")
        await message.reply(
            f"🎆 ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
            f"{HAPPY} Դուք ստացաք {DICE} և շահեցիք՝ NFT:\n"
            f"{GIFT} Ընտրեք ձեր NFT մրցանակը։\n"
            f"{MESSAGE} Մրցանակը ստանալու համար կապ հաստատեք "
            f"@Aleksanyan0001 հետ։\n\n"
            f"{FIRE} Շնորհավորում ենք և մաղթում նոր հաղթանակներ։",
            reply_markup=keyboard.as_markup()
        )


@router.message(F.text.startswith("/add"))
async def add_nft_handler(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Դուք իրավունք չունեք")
        return

    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        await message.answer("Օրինակը՝ /add <nft_number> <nft>")
        return

    try:
        nft_number = int(parts[1])
    except ValueError:
        await message.answer("NFT-ի համարը պետք է լինի թիվ։")
        return

    try:
        save_nft(nft_number, parts[2].strip())
    except sqlite3.IntegrityError:
        await message.answer("Այս NFT համարն արդեն օգտագործվում է։")
        return

    await message.answer(f"NFT ավելացվեց՝ #{nft_number}")


@router.callback_query(F.data.startswith("nft_"))
async def nft_callback(call: CallbackQuery) -> None:
    try:
        nft_data, winner_id = call.data.split(":")
        nft_number = int(nft_data.removeprefix("nft_"))
    except (AttributeError, ValueError):
        await call.answer("❗ Սխալ ընտրություն։", show_alert=True)
        return

    if str(call.from_user.id) != winner_id:
        await call.answer("⛔ Միայն հաղթողը։", show_alert=True)
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT nft FROM NFT_LIST WHERE nft_number = ? AND used = 0",
            (nft_number,)
        ).fetchone()
        if row is None:
            conn.rollback()
            await call.answer("❗ Այս NFT-ն այլևս հասանելի չէ։", show_alert=True)
            return
        conn.execute(
            "UPDATE NFT_LIST SET used = 1 WHERE nft_number = ? AND used = 0",
            (nft_number,)
        )

    await call.message.edit_text(
        f"{GIFT} Ձեր NFT մրցանակը՝ {escape(row[0])}\n"
        f"{MESSAGE} Հարցերի համար կապ հաստատեք @Aleksanyan0001 հետ։"
    )
    await call.answer()


@router.callback_query(F.data.startswith("stars_"))
async def stars_callback(call: CallbackQuery) -> None:
    try:
        data, winner_id = call.data.split(":")
        index = int(data.removeprefix("stars_"))
    except (AttributeError, ValueError):
        await call.answer("❗ Սխալ ընտրություն։", show_alert=True)
        return

    if str(call.from_user.id) != winner_id:
        await call.answer("⛔ Միայն հաղթողը։", show_alert=True)
        return
    if not 0 <= index < 12:
        await call.answer("❗ Սխալ ընտրություն։", show_alert=True)
        return

    values = [generate_win() for _ in range(12)]
    keyboard = InlineKeyboardBuilder()
    for button_index, value in enumerate(values):
        text = f"✅ {value}" if button_index == index else str(value)
        keyboard.button(text=text, callback_data="disabled")
    keyboard.adjust(3, 3, 3, 3)

    await call.message.edit_text(
        f"🎆 ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ, {escape(call.from_user.first_name)}!\n\n"
        f"{FIRE} Դուք բացեցիք և ստացաք {values[index]} {STAR}\n\n"
        f"{MESSAGE} Մրցանակը ստանալու համար կապ հաստատեք "
        f"@Aleksanyan0001 հետ։\n\n"
        f"{CROWN} Շնորհավորում ենք և մաղթում նոր հաղթանակներ։",
        reply_markup=keyboard.as_markup()
    )
    await call.answer()


async def handle(_request: web.Request) -> web.Response:
    return web.Response(text="Bot is running!")


async def web_server() -> None:
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info("Web server started on port %s", port)


async def main() -> None:
    init_db()
    await shopstars.init_db()
    await shopstars.add_all_services()
    logging.info("Starting Aleksanyan bot with shop and slots menus.")
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())
