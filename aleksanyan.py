import asyncio
import random
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Настройки ---
BOT_TOKEN = "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg"   # вставьте токен сюда
DB_PATH = "slots1.db"

oids = [7774684451, 5737457078, 8592719105, -1002042384420, -1004343468249, -1003644333508, 2042384420, 3644333508, 4343468249]

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
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
SEVEN_VALUE = 64              # <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji>

# --- Глобальный режим ---
GAME_MODE = 1  # по умолчанию set1

@router.message(F.text == "/set1")
async def set1_handler(message: Message):
    if message.from_user.id in oids:
        global GAME_MODE
        GAME_MODE = 1
        await message.answer("Ռեժիմ 1: Աստղ (50–100 <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji>-ի ժամանակ, 3-ներ = խրախուսանք արջուկ։)")
    else:
        await message.answer("Դուք իրավունք չունեք")

@router.message(F.text == "/set2")
async def set2_handler(message: Message):
    if message.from_user.id in oids:
        global GAME_MODE
        GAME_MODE = 2
        await message.answer("Ռեժիմ 2։ Միայն NFT (<tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji> = NFT)")
    else:
        await message.answer("Դուք իրավունք չունեք")

# --- 🎰 обработка ---
# --- 🎰 обработка ---
@router.message(F.dice)
async def slot_handler(message: Message):
    if message.dice.emoji != "🎰":
        return

    value = message.dice.value
    save_user(message.from_user.id, message.from_user.full_name)

    if GAME_MODE == 1:
        if value == SEVEN_VALUE:  # <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji>
            kb = InlineKeyboardBuilder()
            for i in range(12):
                kb.button(text="⭐️", callback_data=f"stars_{i}:{message.from_user.id}")
            kb.adjust(3, 3, 3, 3)

            save_win(message.from_user.id, "Stars")
            await message.reply(
                f"<tg-emoji emoji-id='5195100606250889609'>🎆</tg-emoji> ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
                f"<tg-emoji emoji-id='6309567129762926960'>😃</tg-emoji> Դուք ստացաք <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji> և այժմ կարող եք ընտրել <tg-emoji emoji-id='5213035346001955990'>⭐️</tg-emoji> կոճակը՝ պարզելու ձեր հաղթած աստղերը:",
                reply_markup=kb.as_markup()
            )

        elif value in TRIPLE_VALUES:
            await message.reply(
                f"<tg-emoji emoji-id='5415908650214501565'>😔</tg-emoji> Կներեք, {message.from_user.first_name}, ձեզ չընկավ <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji>։\n"
                f"<tg-emoji emoji-id='6275805349626778419'>🎁</tg-emoji> Որպես մխիթարանք դուք ստացաք <tg-emoji emoji-id='5206502842478638898'>🧸</tg-emoji>\n"
                f"<tg-emoji emoji-id='5253742260054409879'>✉️</tg-emoji> Խնդրում ենք կապ հաստատել @Aleksanyan0001"
            )
    elif GAME_MODE == 2:
        if value == SEVEN_VALUE:  # <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji> → NFT
            available_nfts = get_available_nfts()
            if not available_nfts:
                await message.answer("❌ NFT չկա.")
                return

            kb = InlineKeyboardBuilder()
            for nft_number, nft in available_nfts[:6]:
                kb.button(text=f"NFT", callback_data=f"nft_{nft_number}:{message.from_user.id}", style="primary")
            kb.adjust(3, 3)
            save_win(message.from_user.id, "NFT")
            await message.reply(
                f"<tg-emoji emoji-id='5195100606250889609'>🎆</tg-emoji> ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
                f"<tg-emoji emoji-id='6309567129762926960'>😃</tg-emoji> Դուք ստացաք <tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji><tg-emoji emoji-id='5305559532947126301'>🔠</tg-emoji> և շահեցիք՝ NFT:\n<tg-emoji emoji-id='6275805349626778419'>🎁</tg-emoji> Ձեր NFT մրցանակը պահպանված է։\n<tg-emoji emoji-id='5253742260054409879'>✉️</tg-emoji> Մրցանակը ստանալու համար կապ հաստատեք @Aleksanyan0001 հետ։\n\n<tg-emoji emoji-id='5424972470023104089'>🔥</tg-emoji> Շնորհավորում ենք և մաղթում նոր հաղթանակներ։")
        elif value in TRIPLE_VALUES:
            return

@router.message(F.text.startswith("/add"))
async def add_nft_handler(message: Message):
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
            kb.button(text=f"✅ {val}", callback_data="disabled", style="success")
        else:
            kb.button(text=str(val), callback_data="disabled", style="primary")
    kb.adjust(3, 3, 3, 3)


    await call.message.edit_text(
        f"<tg-emoji emoji-id='5195100606250889609'>🎆</tg-emoji> ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ, {call.from_user.first_name}!\n\n"
        f"<tg-emoji emoji-id='5424972470023104089'>🔥</tg-emoji> Դուք բացեցիք և ստացաք {values[index]} <tg-emoji emoji-id='5213035346001955990'>⭐️</tg-emoji>\n\n"
        f"<tg-emoji emoji-id='5253742260054409879'>✉️</tg-emoji> Մրցանակը ստանալու համար կապ հաստատեք @Aleksanyan0001 հետ։\n\n"
        f"<tg-emoji emoji-id='5217822164362739968'>👑</tg-emoji> Շնորհավորում ենք և մաղթում նոր հաղթանակներ։",
        reply_markup=kb.as_markup()
    )

    



# --- Запуск ---
async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(main())
