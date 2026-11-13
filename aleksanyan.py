import asyncio
import os
import random
import sqlite3
from datetime import datetime

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# =========================================================
# SETTINGS
# =========================================================

# Set BOT_TOKEN as an environment variable.
# Do NOT paste your token into a public file.
BOT_TOKEN = os.getenv("BOT_TOKEN", "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg").strip()
DB_PATH = os.getenv("DB_PATH", "slots1.db")

# Only Telegram USER IDs belong here (not channel IDs).
ADMIN_IDS = {
    7774684451,
    5737457078,
    8592719105,
}

CONTACT_USERNAME = "@Aleksanyan0001"

# Add your required channels here.
# Example:
# REQUIRED_CHANNELS = [
#     {"id": -1001234567890, "title": "Our channel",
#      "url": "https://t.me/your_channel"},
# ]
#
# The bot must be an administrator in each channel to reliably
# check membership. Leave [] if you do not want subscription checks.
REQUIRED_CHANNELS = []


# Premium custom emoji IDs found in your uploaded Python file.
EMOJI = {
    "party": "5195100606250889609",   # 🎆
    "star": "5213035346001955990",    # ⭐️
    "crown": "5217822164362739968",   # 👑
    "fire": "5424972470023104089",    # 🔥
    "gift": "6275805349626778419",    # 🎁
    "bear": "5206502842478638898",    # 🧸
    "happy": "6309567129762926960",   # 😃
    "sad": "5415908650214501565",     # 😔
    "letter": "5253742260054409879",  # ✉️
    "slot": "5305559532947126301",    # 🔠 (as found in file)
}

def custom_emoji(key: str, fallback: str) -> str:
    """Return Telegram HTML custom emoji markup."""
    emoji_id = EMOJI.get(key)
    if not emoji_id:
        return fallback
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


# =========================================================
# BOT SETUP
# =========================================================

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is missing. Set the BOT_TOKEN environment variable "
        "before starting the bot."
    )

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML"),
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

GAME_MODE = 1

TRIPLE_VALUES = {1, 22, 43}
SEVEN_VALUE = 64


# =========================================================
# DATABASE
# =========================================================

def db_connect():
    return sqlite3.connect(DB_PATH, timeout=30)


def init_db():
    with db_connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                reg_date TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                win_type TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS NFT_LIST (
                nft_number INTEGER PRIMARY KEY,
                nft TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)


def save_user(user_id: int, full_name: str):
    with db_connect() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, full_name, reg_date)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET full_name = excluded.full_name
            """,
            (user_id, full_name, datetime.now().isoformat()),
        )


def save_win(user_id: int, win_type: str):
    with db_connect() as conn:
        conn.execute(
            "INSERT INTO wins (user_id, win_type, timestamp) VALUES (?, ?, ?)",
            (user_id, win_type, datetime.now().isoformat()),
        )


def save_nft(nft_number: int, nft: str):
    with db_connect() as conn:
        conn.execute(
            """
            INSERT INTO NFT_LIST (nft_number, nft, used, timestamp)
            VALUES (?, ?, 0, ?)
            """,
            (nft_number, nft, datetime.now().isoformat()),
        )


def get_available_nfts():
    with db_connect() as conn:
        return conn.execute(
            """
            SELECT nft_number, nft
            FROM NFT_LIST
            WHERE used = 0
            ORDER BY nft_number
            """
        ).fetchall()


def take_nft(nft_number: int):
    """Atomically reserve an NFT so two users cannot claim the same one."""
    with db_connect() as conn:
        cursor = conn.execute(
            "UPDATE NFT_LIST SET used = 1 WHERE nft_number = ? AND used = 0",
            (nft_number,),
        )
        if cursor.rowcount != 1:
            return None

        row = conn.execute(
            "SELECT nft FROM NFT_LIST WHERE nft_number = ?",
            (nft_number,),
        ).fetchone()
        return row[0] if row else None


init_db()


# =========================================================
# MENUS AND SUBSCRIPTION CHECK
# =========================================================

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Խաղալ")],
            [KeyboardButton(text="ℹ️ Օգնություն")],
        ],
        resize_keyboard=True,
    )


def subscription_keyboard():
    builder = InlineKeyboardBuilder()
    for channel in REQUIRED_CHANNELS:
        builder.row(
            InlineKeyboardButton(
                text=f"📢 Բաժանորդագրվել՝ {channel['title']}",
                url=channel["url"],
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="✅ Ստուգել բաժանորդագրությունը",
            callback_data="check_subscription",
        )
    )
    return builder.as_markup()


async def is_subscribed(user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel["id"],
                user_id=user_id,
            )
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            # Usually means the bot is not an admin or channel ID is wrong.
            return False
    return True


async def require_subscription(message: Message) -> bool:
    if not REQUIRED_CHANNELS:
        return True

    if await is_subscribed(message.from_user.id):
        return True

    await message.answer(
        "Խաղալու համար նախ բաժանորդագրվիր մեր բոլոր ալիքներին։",
        reply_markup=subscription_keyboard(),
    )
    return False


@router.message(F.text == "/start")
async def start_handler(message: Message):
    save_user(message.from_user.id, message.from_user.full_name)

    if REQUIRED_CHANNELS and not await is_subscribed(message.from_user.id):
        await message.answer(
            "👋 Բարի գալուստ։ Խաղալու համար նախ բաժանորդագրվիր ալիքներին։",
            reply_markup=subscription_keyboard(),
        )
        return

    await message.answer(
        "👋 Բարի գալուստ մեր խաղարկություն։\n\n"
        "Սեղմիր «🎰 Խաղալ» և ուղարկիր Telegram-ի 🎰 զառը։\n"
        "Հաջողություն։",
        reply_markup=main_menu(),
    )


@router.message(F.text == "/menu")
async def menu_handler(message: Message):
    if not await require_subscription(message):
        return
    await message.answer("📋 Գլխավոր մենյու", reply_markup=main_menu())


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(call: CallbackQuery):
    if await is_subscribed(call.from_user.id):
        await call.message.edit_text(
            "✅ Բաժանորդագրությունը հաստատված է։\n"
            "Ուղարկիր /start՝ խաղի մենյուն բացելու համար։"
        )
        await call.answer("Բաժանորդագրությունը հաստատված է։")
    else:
        await call.answer(
            "Դեռ բոլոր ալիքներին բաժանորդագրված չես։",
            show_alert=True,
        )


@router.message(F.text == "🎰 Խաղալ")
async def play_handler(message: Message):
    if not await require_subscription(message):
        return
    await message.answer("🎰 Խաղալու համար ուղարկիր Telegram-ի 🎰 զառը։")


@router.message(F.text == "ℹ️ Օգնություն")
async def help_handler(message: Message):
    if not await require_subscription(message):
        return
    await message.answer(
        "ℹ️ Օգնություն\n\n"
        "1. Սեղմիր «Խաղալ»։\n"
        "2. Ուղարկիր 🎰 զառը։\n"
        "3. Հաղթելու դեպքում ընտրիր մրցանակը։\n\n"
        f"Հարցերի համար՝ {CONTACT_USERNAME}"
    )


# =========================================================
# ADMIN COMMANDS
# =========================================================

@router.message(F.text == "/set1")
async def set1_handler(message: Message):
    global GAME_MODE

    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Դուք իրավունք չունեք։")
        return

    GAME_MODE = 1
    await message.answer(
        "✅ Ռեժիմ 1-ը միացված է։\n"
        f"{custom_emoji('star', '⭐️')} Աստղեր՝ 50–100։\n"
        "Երեք նույն նշանների դեպքում՝ 🧸 խրախուսական մրցանակ։"
    )


@router.message(F.text == "/set2")
async def set2_handler(message: Message):
    global GAME_MODE

    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Դուք իրավունք չունեք։")
        return

    GAME_MODE = 2
    await message.answer(
        "✅ Ռեժիմ 2-ը միացված է։\n"
        "🎰 Հաղթանակի դեպքում՝ NFT։"
    )


@router.message(F.text.startswith("/add"))
async def add_nft_handler(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Դուք իրավունք չունեք։")
        return

    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("Օրինակ՝ /add 1 https://example.com/nft")
            return

        nft_number = int(parts[1])
        nft_value = parts[2].strip()
        if not nft_value:
            await message.answer("NFT հղումը կամ տվյալը դատարկ է։")
            return

        save_nft(nft_number, nft_value)
        await message.answer(
            f"✅ NFT-ն ավելացվեց։\nՀամար՝ #{nft_number}\nՏվյալ՝ {nft_value}"
        )

    except sqlite3.IntegrityError:
        await message.answer("❌ Այս NFT համարն արդեն գոյություն ունի։")
    except ValueError:
        await message.answer("❌ NFT համարը պետք է լինի թիվ։")
    except Exception as exc:
        await message.answer(f"⚠️ Սխալ՝ {exc}")


# =========================================================
# SLOT GAME
# =========================================================

def generate_win() -> int:
    roll = random.random()
    if roll <= 0.90:
        return random.choice([50, 55, 60])
    if roll <= 0.99:
        return random.choice([60, 65, 70])
    if roll <= 0.9900000005:
        return random.choice([70, 75, 80])
    return random.choice([80, 85, 90, 95, 100])


@router.message(F.dice)
async def slot_handler(message: Message):
    if message.dice.emoji != "🎰":
        return

    if REQUIRED_CHANNELS and not await is_subscribed(message.from_user.id):
        await message.reply(
            "Խաղալու համար նախ բաժանորդագրվիր ալիքներին։",
            reply_markup=subscription_keyboard(),
        )
        return

    user_id = message.from_user.id
    save_user(user_id, message.from_user.full_name)
    value = message.dice.value

    if GAME_MODE == 1:
        if value == SEVEN_VALUE:
            keyboard = InlineKeyboardBuilder()
            for index in range(12):
                # Telegram inline button labels use ordinary emoji text.
                keyboard.button(
                    text="⭐️",
                    callback_data=f"stars_{index}:{user_id}",
                )
            keyboard.adjust(3, 3, 3, 3)

            save_win(user_id, "Stars")
            await message.reply(
                f"{custom_emoji('party', '🎆')} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ։</b>\n\n"
                f"{custom_emoji('happy', '😃')} Դու շահել ես։ "
                "Ընտրիր աստղերից մեկը՝ մրցանակդ պարզելու համար։",
                reply_markup=keyboard.as_markup(),
            )

        elif value in TRIPLE_VALUES:
            await message.reply(
                f"{custom_emoji('sad', '😔')} Կներես, "
                f"{message.from_user.first_name}, այս անգամ չշահեցիր։\n"
                f"{custom_emoji('gift', '🎁')} Որպես մխիթարանք՝ 🧸։\n"
                f"{custom_emoji('letter', '✉️')} Կապ՝ {CONTACT_USERNAME}"
            )

    elif GAME_MODE == 2:
        if value == SEVEN_VALUE:
            available_nfts = get_available_nfts()

            if not available_nfts:
                await message.reply("❌ Այս պահին ազատ NFT-ներ չկան։")
                return

            keyboard = InlineKeyboardBuilder()
            for nft_number, _nft in available_nfts[:6]:
                keyboard.button(
                    text=f"🎁 NFT #{nft_number}",
                    callback_data=f"nft_{nft_number}:{user_id}",
                )
            keyboard.adjust(2, 2, 2)

            save_win(user_id, "NFT")
            await message.reply(
                f"{custom_emoji('party', '🎆')} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ։</b>\n\n"
                f"{custom_emoji('happy', '😃')} Դու շահել ես NFT խաղարկությունը։\n"
                "Ընտրիր քո NFT-ն։",
                reply_markup=keyboard.as_markup(),
            )


# =========================================================
# STAR SELECTION
# =========================================================

@router.callback_query(F.data.startswith("stars_"))
async def stars_callback(call: CallbackQuery):
    try:
        data, winner_id = call.data.split(":", maxsplit=1)
        if str(call.from_user.id) != winner_id:
            await call.answer("⛔ Միայն հաղթողը կարող է ընտրել։", show_alert=True)
            return

        index = int(data.split("_", maxsplit=1)[1])
        if not 0 <= index < 12:
            await call.answer("Անվավեր ընտրություն։", show_alert=True)
            return

        values = [generate_win() for _ in range(12)]
        keyboard = InlineKeyboardBuilder()

        for i, amount in enumerate(values):
            label = f"✅ {amount} ⭐️" if i == index else f"{amount} ⭐️"
            keyboard.button(text=label, callback_data="already_opened")
        keyboard.adjust(3, 3, 3, 3)

        await call.message.edit_text(
            f"{custom_emoji('party', '🎆')} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ, "
            f"{call.from_user.first_name}։</b>\n\n"
            f"{custom_emoji('fire', '🔥')} Քո մրցանակն է՝ "
            f"{values[index]} {custom_emoji('star', '⭐️')}\n\n"
            f"{custom_emoji('letter', '✉️')} Մրցանակը ստանալու համար կապ՝ "
            f"{CONTACT_USERNAME}\n\n"
            f"{custom_emoji('crown', '👑')} Շնորհավորում ենք։",
            reply_markup=keyboard.as_markup(),
        )
        await call.answer()

    except Exception:
        await call.answer("Չհաջողվեց բացել մրցանակը։", show_alert=True)


@router.callback_query(F.data == "already_opened")
async def already_opened_callback(call: CallbackQuery):
    await call.answer("Այս ընտրությունն արդեն բացված է։")


# =========================================================
# NFT SELECTION
# =========================================================

@router.callback_query(F.data.startswith("nft_"))
async def nft_callback(call: CallbackQuery):
    try:
        data, winner_id = call.data.split(":", maxsplit=1)
        if str(call.from_user.id) != winner_id:
            await call.answer(
                "⛔ Այս NFT-ն կարող է ընտրել միայն հաղթողը։",
                show_alert=True,
            )
            return

        nft_number = int(data.split("_", maxsplit=1)[1])
        nft = take_nft(nft_number)

        if nft is None:
            await call.answer(
                "❌ Այս NFT-ն արդեն վերցված է կամ գոյություն չունի։",
                show_alert=True,
            )
            return

        await call.message.edit_text(
            f"{custom_emoji('party', '🎆')} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ։</b>\n\n"
            f"{custom_emoji('gift', '🎁')} Քո NFT-ն՝ #{nft_number}\n\n"
            f"🔗 {nft}\n\n"
            f"{custom_emoji('letter', '✉️')} Հարցերի համար՝ {CONTACT_USERNAME}"
        )
        await call.answer("NFT-ն հաջողությամբ ընտրվեց։")

    except Exception:
        await call.answer("Չհաջողվեց ընտրել NFT-ն։", show_alert=True)


# =========================================================
# HTTP SERVER (OPTIONAL, FOR HOSTING)
# =========================================================

async def handle(request):
    return web.Response(text="Bot is running!")


async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", "8080"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")


# =========================================================
# START
# =========================================================

async def main():
    print("Bot is starting...")
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
