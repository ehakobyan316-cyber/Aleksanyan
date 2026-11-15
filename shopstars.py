import logging
from datetime import datetime
import aiosqlite
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import random

# ---------- КОНФИГ ----------
ADMIN_ID = [8950790565, 7774684451]
GIFT_OWNER_ID = 7774684451
DB_PATH = "botdonate10.db"

logging.basicConfig(level=logging.INFO)

router = Router(name="shopstars_router")

user_states = {}
user_brands = {}
user_deposits = {}

fire_emoji = "5368324170671202286"
star_emoji = "5951810621887484519"
money_emoji = "5224257782013769471"
dice_emoji = "5368361284419201529"
cart_emoji = "5368297072938459416"
check_emoji = "5368324170671202287"
key_emoji = "5368348632158490520"

nazad = "5314444424418192113"
about = fire_emoji
spisok = cart_emoji
patm = check_emoji
b = money_emoji
pop = star_emoji
prov = check_emoji
buy = cart_emoji
nastr = key_emoji
shop = check_emoji
donat = star_emoji
roz = "5449800250032143374"
chroz = "5443038326535759644"
otziv = "5467538555158943525"
hast = check_emoji
chex = "5210952531676504517"

# ---------- СПИСОК БРЕНДОВ ----------
BRANDS = ["Samsung", "iPhone", "Redmi", "ZTE", "OPPO", "OnePlus", "Realme", "Huawei", "Honor", "Tecno"]

# ---------- СПИСКИ МОДЕЛЕЙ ----------
MODELS = {
    "Samsung": [
        "Galaxy A15", "Galaxy A25", "Galaxy A35", "Galaxy A55",
        "Galaxy A54", "Galaxy A53", "Galaxy A34", "Galaxy A33",
        "Galaxy A14", "Galaxy A13", "Galaxy A12", "Galaxy A11",
        "Galaxy M14", "Galaxy M13", "Galaxy M12", "Galaxy M33", "Galaxy M23",
        "Galaxy S24 Ultra", "Galaxy S24", "Galaxy S23 Ultra", "Galaxy S23",
        "Galaxy S22 Ultra", "Galaxy Z Flip5", "Galaxy Z Fold5", "Galaxy Z Flip4"
    ],
    "iPhone": [
        "iPhone 16 Pro Max", "iPhone 16 Pro", "iPhone 16",
        "iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15",
        "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14",
        "iPhone 13 Pro Max", "iPhone 13 Pro", "iPhone 13",
        "iPhone 12 Pro Max", "iPhone 12 Pro", "iPhone 12",
        "iPhone 11 Pro Max", "iPhone 11 Pro", "iPhone 11",
        "iPhone SE 2022", "iPhone SE 2020", "iPhone XR",
        "iPhone XS Max", "iPhone XS", "iPhone X", "iPhone 8 Plus"
    ],
    "Redmi": [
        "Redmi Note 13 Pro+", "Redmi Note 13 Pro", "Redmi Note 13",
        "Redmi Note 12 Pro+", "Redmi Note 12 Pro", "Redmi Note 12",
        "Redmi Note 11 Pro+", "Redmi Note 11 Pro", "Redmi Note 11",
        "Redmi Note 10 Pro", "Redmi Note 10", "Redmi Note 9 Pro", "Redmi Note 9",
        "Redmi Note 8 Pro", "Redmi Note 8", "Redmi Note 7 Pro", "Redmi Note 7",
        "Redmi 13C", "Redmi 12C", "Redmi 10C", "Redmi 9C",
        "Redmi 8A", "Redmi 7A", "Redmi K70 Pro", "Redmi K60 Pro"
    ],
    "ZTE": [
        "ZTE Nubia Red Magic 9 Pro", "ZTE Nubia Red Magic 9",
        "ZTE Nubia Red Magic 8 Pro", "ZTE Nubia Red Magic 8",
        "ZTE Nubia Z70 Ultra", "ZTE Nubia Z60 Ultra", "ZTE Nubia Z50 Ultra",
        "ZTE Nubia Z40 Pro", "ZTE Axon 50 Ultra", "ZTE Axon 40 Ultra",
        "ZTE Axon 30 Ultra", "ZTE Axon 20", "ZTE Blade V70", "ZTE Blade V60",
        "ZTE Blade V50", "ZTE Blade V40", "ZTE Blade V30", "ZTE Blade A73",
        "ZTE Blade A72", "ZTE Blade A71", "ZTE Blade A51", "ZTE Blade A31",
        "ZTE Blade A21", "ZTE Blade A11", "ZTE Blade A7"
    ],
    "OPPO": [
        "Oppo Find X7 Ultra", "Oppo Find X7 Pro", "Oppo Find X6 Pro", "Oppo Find X6",
        "Oppo Find N3 Flip", "Oppo Find N3", "Oppo Reno 12 Pro", "Oppo Reno 12",
        "Oppo Reno 11 Pro", "Oppo Reno 11", "Oppo Reno 10 Pro+", "Oppo Reno 10 Pro",
        "Oppo Reno 10", "Oppo Reno 9 Pro", "Oppo Reno 9", "Oppo Reno 8 Pro",
        "Oppo Reno 8", "Oppo Reno 7 Pro", "Oppo Reno 7", "Oppo Reno 6 Pro",
        "Oppo Reno 6", "Oppo A98", "Oppo A78", "Oppo A58", "Oppo A38"
    ],
    "OnePlus": [
        "OnePlus 12", "OnePlus 12R", "OnePlus 11", "OnePlus 11R",
        "OnePlus 10 Pro", "OnePlus 10T", "OnePlus 10R", "OnePlus 9 Pro",
        "OnePlus 9", "OnePlus 9R", "OnePlus 8 Pro", "OnePlus 8T", "OnePlus 8",
        "OnePlus 7 Pro", "OnePlus 7T", "OnePlus 7", "OnePlus 6T", "OnePlus 6",
        "OnePlus Nord 3", "OnePlus Nord 2T", "OnePlus Nord 2",
        "OnePlus Nord CE 3", "OnePlus Nord CE 2", "OnePlus Nord CE",
        "OnePlus Open"
    ],
    "Realme": [
        "Realme GT 7 Pro", "Realme GT 7", "Realme GT 6 Pro", "Realme GT 6",
        "Realme GT Neo 6", "Realme GT Neo 5", "Realme GT Neo 3", "Realme GT Neo 2",
        "Realme GT Master Edition", "Realme 12 Pro+", "Realme 12 Pro", "Realme 12",
        "Realme 11 Pro+", "Realme 11 Pro", "Realme 11", "Realme 10 Pro+",
        "Realme 10 Pro", "Realme 10", "Realme 9 Pro+", "Realme 9 Pro", "Realme 9",
        "Realme C55", "Realme C53", "Realme C33", "Realme Narzo 60 Pro"
    ],
    "Huawei": [
        "Huawei Pura 70 Ultra", "Huawei Pura 70 Pro", "Huawei Pura 70",
        "Huawei P60 Pro", "Huawei P60", "Huawei P50 Pro", "Huawei P50",
        "Huawei Mate 60 Pro+", "Huawei Mate 60 Pro", "Huawei Mate 60",
        "Huawei Mate 50 Pro", "Huawei Mate 50", "Huawei Mate 40 Pro", "Huawei Mate 40",
        "Huawei Mate X5", "Huawei Mate X3", "Huawei Mate X2", "Huawei nova 12 Pro",
        "Huawei nova 12", "Huawei nova 11 Pro", "Huawei nova 11", "Huawei nova 10 Pro",
        "Huawei nova 10", "Huawei Y9a", "Huawei Y7a"
    ],
    "Honor": [
        "Honor Magic6 Pro", "Honor Magic6", "Honor Magic6 Lite",
        "Honor Magic5 Pro", "Honor Magic5", "Honor Magic5 Lite",
        "Honor Magic4 Pro", "Honor Magic4", "Honor Magic4 Lite",
        "Honor Magic3 Pro", "Honor Magic3", "Honor Magic3 Lite",
        "Honor 100 Pro", "Honor 100", "Honor 90 Pro", "Honor 90",
        "Honor 80 Pro", "Honor 80", "Honor 70 Pro", "Honor 70",
        "Honor X50", "Honor X40", "Honor X30", "Honor Play 40",
        "Honor Play 30"
    ]
}


# ---------- БАЗА ДАННЫХ ----------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS processed_gifts (
            gift_key TEXT PRIMARY KEY,
            user_id INTEGER,
            stars INTEGER,
            created_at TEXT
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS processed_payments (
            payment_charge_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            stars INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS balance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tx_type TEXT,
            amount INTEGER,
            partner_desc TEXT,
            created_at TEXT
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_name TEXT,
            stars_spent INTEGER,
            status TEXT,
            service_status TEXT,
            created_at TEXT
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            service_status TEXT DEFAULT 'Թույլ'
        )""")
        await db.commit()


# ---------- УТИЛИТЫ ----------
def gift_key(g: dict) -> str:
    sender = (g.get("sender_user") or {}).get("id", 0)
    gift_id = (g.get("gift") or {}).get("id", "")
    return f"{sender}:{gift_id}:{g.get('send_date', 0)}"


async def collect_owner_gifts() -> list[dict]:
    raise NotImplementedError("Նվերներով ավտոմատ լիցքավորումը դեռ միացված չէ։")


async def check_gift_donation(user_id: int) -> dict:
    res = {"credited": 0, "stars": 0, "unique": 0}
    gifts = await collect_owner_gifts()
    for g in gifts:
        if (g.get("sender_user") or {}).get("id") != user_id:
            continue
        if g.get("type") != "regular":
            res["unique"] += 1
            continue
        key = gift_key(g)
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT 1 FROM processed_gifts WHERE gift_key = ?", (key,)) as cur:
                if await cur.fetchone():
                    continue
            stars = int((g.get("gift") or {}).get("star_count") or 0)
            if stars <= 0:
                continue
            await db.execute(
                "INSERT INTO processed_gifts (gift_key, user_id, stars, created_at) VALUES (?,?,?,?)",
                (key, user_id, stars, datetime.now().isoformat())
            )
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (stars, user_id))
            await db.execute(
                "INSERT INTO balance_history (user_id, tx_type, amount, partner_desc, created_at) VALUES (?,?,?,?,?)",
                (user_id, "Դոնատ նվերներով", stars, f"{stars} աստղ", datetime.now().isoformat())
            )
            await db.commit()
            res["credited"] += stars
            res["stars"] += stars
    return res


def channels_kb():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Ալիք` Aleksanyan FF Shop", style="primary", icon_custom_emoji_id=shop),
             KeyboardButton(text="Ալիք` Aleksanyan DONAT", style="primary", icon_custom_emoji_id=donat)],

            [KeyboardButton(text="Ալիք` Aleksanyan Розыгрыш", style="primary", icon_custom_emoji_id=roz),
             KeyboardButton(text="Չատ` Чат Aleksanyan FF Shop", style="primary", icon_custom_emoji_id=chroz)],

            [KeyboardButton(text="Ալիք` отзывы Aleksanyan FF SHOP", style="primary", icon_custom_emoji_id=otziv)]
        ]
    )


# ---------- ЛОГИКА ПОКУПКИ ----------
async def try_purchase_service(user_id: int, service_name: str, service_status: str = "Թույլ") -> dict:
    status_prices = {"Թույլ": 150, "Միջին": 200, "VIP": 250}
    price = status_prices.get(service_status, 150)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        balance = row[0] if row else 0

        if balance >= price:
            result = await db.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
                (price, user_id, price)
            )
            if result.rowcount != 1:
                await db.rollback()
                return {"status": "pending", "needed": price, "status_level": service_status}
            await db.execute(
                "INSERT INTO purchases (user_id, service_name, stars_spent, status, service_status, created_at) VALUES (?,?,?,?,?,?)",
                (user_id, service_name, price, "Հաջողված", service_status, datetime.now().isoformat())
            )
            await db.commit()
            return {"status": "success", "service": service_name, "status_level": service_status}
        else:
            await db.rollback()
            return {"status": "pending", "needed": price - balance, "status_level": service_status}


async def add_all_services():
    async with aiosqlite.connect(DB_PATH) as db:
        for brand, models in MODELS.items():
            for model in models:
                service_name = f"{brand} {model}"
                await db.execute(
                    "INSERT INTO services (name, price) "
                    "SELECT ?, 150 WHERE NOT EXISTS "
                    "(SELECT 1 FROM services WHERE name = ?)",
                    (service_name, service_name)
                )
        await db.commit()


# ---------- МЕНЮ ----------
def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="Ցուցակ", callback_data="buy_service", style="success", icon_custom_emoji_id=spisok)
    )
    kb.row(
        InlineKeyboardButton(text="Բալանս", callback_data="check_balance", style="success", icon_custom_emoji_id=b),
        InlineKeyboardButton(text="Պատմություն", callback_data="history_menu", style="danger", icon_custom_emoji_id=patm)
    )
    kb.row(InlineKeyboardButton(text="Մեր մասին", callback_data="about", style="primary", icon_custom_emoji_id=about))
    kb.row(
        InlineKeyboardButton(
            text="Խաղալ",
            callback_data="play_slots",
            style="primary",
            icon_custom_emoji_id=dice_emoji
        )
    )
    return kb.as_markup()


@router.message(F.text == "/start")
async def start_cmd(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)",
                         (message.from_user.id, message.from_user.username))
        await db.commit()
    await message.answer(
        "<tg-emoji emoji-id='5217822164362739968'>👑</tg-emoji> Բարի գալուստ, ընտրի՜ր։",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )
    await message.answer(
        "Բաժանորդագրվելու համար ընտրեք ալիքը՝",
        reply_markup=channels_kb()
    )


# ---------- КОМАНДА /addb ----------
@router.message(F.text.startswith("/addb"))
async def add_balance_cmd(message: Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer("⛔️ Չկա իրավունք։")
        return

    try:
        _, data = message.text.split(" ", 1)
        user_id_str, amount_str = data.split(";")
        user_id = int(user_id_str.strip())
        amount = int(amount_str.strip())
    except Exception:
        await message.answer("⚠️ Օրինակ` /addb user_id;amount")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()

        if not row:
            await message.answer(f"❗ {user_id} չկա։")
            return

        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

    await message.answer(f"✅ {user_id} + {amount}:")


# ---------- ABOUT ----------
@router.callback_query(F.data == "about")
async def about_info(callback: CallbackQuery):
    await callback.message.answer(
        "Ընտրիր ներքևում`",
        reply_markup=channels_kb(),
        parse_mode="html"
    )
    await callback.answer()


# ---------- КАНАЛЫ ----------
channel_map = {
    "Ալիք` Aleksanyan FF Shop": {
        "url": "https://t.me/Aleksanyanffshop",
        "photo": "https://imgur.com/a/2shllGI"
    },
    "Ալիք` Aleksanyan DONAT": {
        "url": "https://t.me/AleksanyanDONAT",
        "photo": "https://imgur.com/a/e1OJrgv"
    },
    "Ալիք` Aleksanyan Розыгрыш": {
        "url": "https://t.me/AleksanyanNverner",
        "photo": "https://imgur.com/a/PAmYARn"
    },
    "Չատ` Чат Aleksanyan FF Shop": {
        "url": "https://t.me/AleksanyanChat",
        "photo": "https://imgur.com/a/2shllGI"
    },
    "Ալիք` отзывы Aleksanyan FF SHOP": {
        "url": "https://t.me/Aleksanyanffshopp",
        "photo": "https://imgur.com/a/n06xwWS"
    }
}


@router.message(F.text.in_(channel_map.keys()))
async def channel_info(message: Message):
    data = channel_map.get(message.text)
    if not data:
        await message.answer("❗️ Канал не найден")
        return

    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="Տեսնել",
            url=data["url"],
            style="success"
        )
    )
    kb.row(
        InlineKeyboardButton(
            text="Հետ",
            callback_data="main_menu",
            style="primary",
            icon_custom_emoji_id=nazad
        )
    )

    await message.answer_photo(
        photo=data["photo"],
        reply_markup=kb.as_markup()
    )


# ---------- ИСТОРИЯ ----------
@router.callback_query(F.data == "history_menu")
async def history_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="Լիցքավորումներ", callback_data="history_deposits", style="success", icon_custom_emoji_id=pop),
        InlineKeyboardButton(text="Գնումներ", callback_data="history_purchases", style="danger", icon_custom_emoji_id=b)
    )
    kb.row(InlineKeyboardButton(text="Հետ", callback_data="main_menu", style="primary", icon_custom_emoji_id=nazad))
    await callback.message.edit_text("Պատմություն", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "history_deposits")
async def history_deposits(callback: CallbackQuery):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT tx_type, amount, partner_desc, created_at FROM balance_history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
            (callback.from_user.id,)
        ) as cur:
            history = await cur.fetchall()
    if not history:
        await callback.message.edit_text("❗️ Լիցքավորումներ չկան։")
    else:
        lines = ["<tg-emoji emoji-id='5224257782013769471'>💰</tg-emoji> <b>Լիցքավորումներ`</b>"]
        for tx_type, amount, desc, created_at in history:
            lines.append(f"{created_at} | {tx_type} | +{amount} | {desc}")
        await callback.message.edit_text("\n".join(lines), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "history_purchases")
async def history_purchases(callback: CallbackQuery):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT service_name, stars_spent, status, service_status, created_at FROM purchases WHERE user_id = ? ORDER BY id DESC LIMIT 10",
            (callback.from_user.id,)
        ) as cur:
            purchases = await cur.fetchall()

    if not purchases:
        await callback.message.edit_text("❗️Գնումներ չկան։")
    else:
        lines = ["<tg-emoji emoji-id='5359681227592854334'>❤️</tg-emoji> <b>Գնումներ`</b>"]
        for name, spent, status, service_status, created_at in purchases:
            try:
                dt = datetime.fromisoformat(created_at)
                formatted_date = dt.strftime("%H:%M:%S, %d.%m.%y")
            except Exception:
                formatted_date = created_at
            lines.append(f"{formatted_date} | {name} | -{spent} | {service_status} | {status}")
        await callback.message.edit_text("\n".join(lines), parse_mode="HTML")

    await callback.answer()


# ---------- ДОНАТ ПОДАРКОМ ----------
@router.callback_query(F.data == "donate_gift")
async def donate_gift_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Ես ուղարկել եմ", callback_data="gift_check"))
    kb.row(InlineKeyboardButton(text="Հետ", callback_data="main_menu", style="primary", icon_custom_emoji_id=nazad))
    await callback.message.edit_text(
        f"<tg-emoji emoji-id='5951810621887484519'>⭐️</tg-emoji> Դոնատ նվերով\n\n"
        f"1. Ուղարկիր նվեր <a href='tg://user?id={GIFT_OWNER_ID}'>վաճառողին</a>.\n"
        f"2. Սեղմիր «Ես ուղարկել եմ»:",
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    await callback.answer()


# ---------- ПРОВЕРКА БАЛАНСА ----------
@router.callback_query(F.data == "check_balance")
async def check_balance(callback: CallbackQuery):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (callback.from_user.id,)) as cur:
            row = await cur.fetchone()
    balance = row[0] if row else 0

    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="Լիցքավորել",
            callback_data="deposit_stars",
            style="success",
            icon_custom_emoji_id=pop
        ),
        InlineKeyboardButton(
            text="Հետ",
            callback_data="main_menu",
            style="primary",
            icon_custom_emoji_id=nazad
        )
    )
    await callback.message.edit_text(
        f"<tg-emoji emoji-id='5224257782013769471'>💰</tg-emoji> Ձեր բալանսը` {balance} <tg-emoji emoji-id='5951810621887484519'>⭐️</tg-emoji>",
        reply_markup=kb.as_markup(),
        parse_mode="html"
    )
    await callback.answer()


@router.callback_query(F.data == "gift_check")
async def gift_check_cb(callback: CallbackQuery):
    wait = await callback.message.edit_text("🔎 Նվերների ստուգում...")
    try:
        res = await check_gift_donation(callback.from_user.id)
    except NotImplementedError as exc:
        logging.warning("Gift deposit check is unavailable: %s", exc)
        await wait.edit_text(f"❗ {exc}")
        await callback.answer()
        return
    if "error" in res:
        await wait.edit_text(f"❗️ Խնդիր` {res['error']}")
        await callback.answer()
        return
    if res["credited"] == 0:
        await wait.edit_text("❗️ Նոր նվերներ չի գտնվել։")
    else:
        await wait.edit_text(
            f"Գտնվեց {res['stars']} <tg-emoji emoji-id='{star_emoji}'>⭐️</tg-emoji>!\nԲալանսը լիցքավորվեց։",
            parse_mode="HTML"
        )
    await callback.answer()


# ---------- МЕНЮ ПОКУПОК ----------
@router.callback_query(F.data == "buy_service")
async def buy_service_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for brand in BRANDS:
        kb.button(text=brand, callback_data=f"brand_{brand}", style="danger")

    kb.adjust(3)
    kb.row(InlineKeyboardButton(text="Հետ", callback_data="main_menu", style="primary", icon_custom_emoji_id=nazad))

    await callback.message.edit_text(
        "<tg-emoji emoji-id='5276323870951886980'>📱</tg-emoji> Ընտրիր բրենդը:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("status_"))
async def change_model_status(callback: CallbackQuery):
    service_name = callback.data.replace("status_", "")

    kb = callback.message.reply_markup.inline_keyboard
    current_status = "Թույլ"
    for row in kb:
        for btn in row:
            if btn.callback_data == f"status_{service_name}":
                if "Թույլ" in btn.text:
                    current_status = "Թույլ"
                elif "Միջին" in btn.text:
                    current_status = "Միջին"
                elif "VIP" in btn.text:
                    current_status = "VIP"

    next_status = {"Թույլ": "Միջին", "Միջին": "VIP", "VIP": "Թույլ"}[current_status]

    for row in kb:
        for btn in row:
            if btn.callback_data == f"status_{service_name}":
                btn.text = f"Նաստր: {next_status}"

    await callback.message.edit_reply_markup(reply_markup=callback.message.reply_markup)
    await callback.answer(f"Նաստր {service_name} փոխվեց՝ {next_status}")


# ---------- ВЫБОР БРЕНДА ----------
@router.callback_query(F.data.startswith("brand_"))
async def brand_selected(callback: CallbackQuery):
    brand = callback.data.replace("brand_", "")
    if brand not in MODELS:
        await callback.answer("❗ Անհայտ բրենդ։", show_alert=True)
        return
    user_brands[callback.from_user.id] = brand
    user_states[callback.from_user.id] = "await_model"

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Հետ", callback_data="buy_service", style="primary", icon_custom_emoji_id=nazad))

    await callback.message.edit_text(
        f"<tg-emoji emoji-id='5276323870951886980'>📱</tg-emoji> Դուք ընտրեցիք {brand}։\n\n<tg-emoji emoji-id='5402594127042847701'>💬</tg-emoji> Գրեք ձեր մոդելը`",
        reply_markup=kb.as_markup(), parse_mode="html"
    )
    await callback.answer()


@router.callback_query(F.data == "deposit_stars")
async def deposit_stars(callback: CallbackQuery):
    await callback.message.edit_text("<tg-emoji emoji-id='5402594127042847701'>💬</tg-emoji>Գրեք աստղերի քանակը։", parse_mode="html")
    user_states[callback.from_user.id] = "await_amount"
    await callback.answer()


# ---------- ВВОД МОДЕЛИ ИЛИ СУММЫ ----------
@router.message(F.text)
async def universal_input(message: Message):
    state = user_states.get(message.from_user.id)
    if not state:
        return

    if state == "await_model":
        brand = user_brands.get(message.from_user.id)
        if not brand:
            return
        model_input = message.text.strip()
        model = next(
            (item for item in MODELS[brand] if item.casefold() == model_input.casefold()),
            None
        )
        if model is None:
            await message.answer(
                f"❗ Այդ մոդելը չկա {brand}-ի ցանկում։ Գրեք մոդելի ամբողջական անունը։"
            )
            return
        service_name = f"{brand} {model}"

        kb = InlineKeyboardBuilder()
        kb.row(
            InlineKeyboardButton(text="Ստուգել բալանս", callback_data="check_balance", style="danger", icon_custom_emoji_id=prov),
            InlineKeyboardButton(text="Գնել", callback_data=f"buyid_{service_name}", style="success", icon_custom_emoji_id=buy)
        )
        kb.row(InlineKeyboardButton(text="Նաստր: Թույլ", callback_data=f"status_{service_name}", style="danger", icon_custom_emoji_id=nastr))
        kb.row(InlineKeyboardButton(text="Հետ", callback_data="buy_service", style="primary", icon_custom_emoji_id=nazad))

        await message.answer(
            f"Սեղմեք «Գնել», որպեսզի գնել «{service_name}»-ի նաստրը։",
            reply_markup=kb.as_markup()
        )
        user_states.pop(message.from_user.id, None)

    elif state == "await_amount":
        try:
            amount = int(message.text.strip())
            if amount <= 0:
                raise ValueError
        except Exception:
            await message.answer("❗ Գրեք թիվ։")
            return

        user_deposits[message.from_user.id] = {"step": "confirm", "amount": amount}
        kb = InlineKeyboardBuilder()
        kb.row(
            InlineKeyboardButton(text="Հաստատել", callback_data="confirm_deposit", style="success", icon_custom_emoji_id=hast),
            InlineKeyboardButton(text="Չեղարկել", callback_data="main_menu", style="primary", icon_custom_emoji_id=chex)
        )
        await message.answer(
            f"Դուք ցանկանում եք լիցքավորել {amount} "
            f"<tg-emoji emoji-id='{star_emoji}'>⭐️</tg-emoji>?",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        user_states.pop(message.from_user.id, None)


@router.callback_query(F.data.startswith("buyid_"))
async def buy_service_action(callback: CallbackQuery):
    service_name = callback.data.replace("buyid_", "")

    kb = callback.message.reply_markup.inline_keyboard
    current_status = "Թույլ"
    for row in kb:
        for btn in row:
            if btn.callback_data == f"status_{service_name}":
                if "Թույլ" in btn.text:
                    current_status = "Թույլ"
                elif "Միջին" in btn.text:
                    current_status = "Միջին"
                elif "VIP" in btn.text:
                    current_status = "VIP"

    result = await try_purchase_service(callback.from_user.id, service_name, current_status)

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Հետ", callback_data="buy_service", style="primary", icon_custom_emoji_id=nazad))

    abzor = random.randint(100, 200)
    kolim = random.randint(100, 200)
    x2 = random.randint(100, 200)
    x4 = random.randint(100, 200)
    sniper = random.randint(100, 200)
    achq = random.randint(100, 200)
    knopka = random.randint(37, 62)
    dpi = random.randint(400, 720) if "iPhone" not in service_name else None

    config_text = (
        f"<tg-emoji emoji-id='5276323870951886980'>📱</tg-emoji> {service_name}\n"
        f"Նաստր: {result.get('status_level', 'Թույլ')}\n\n"
        f"Обзор: {abzor}\n"
        f"Коллиматор: {kolim}\n"
        f"2x Прицел: {x2}\n"
        f"4x Прицел: {x4}\n"
        f"Снайперский Прицел: {sniper}\n"
        f"Свободный Обзор: {achq}\n\n"
        f"Кнопка: {knopka}\n"
        f"DPI: {dpi if dpi else 'iPhone (չկա dpi)'}"
    )

    if result["status"] == "success":
        config_text += f"\n\n✅ «{service_name}» ({result['status_level']}) հաջողությամբ գնված է!"
    elif result["status"] == "pending":
        config_text = f"\n\n❗️ Անբավարար աստղեր` {result['needed']} (պահանջվում է {result['status_level']} գին)"
    else:
        config_text = f"\n\n⚠️ Խնդիր` {result.get('msg', '')}"

    await callback.message.edit_text(config_text, reply_markup=kb.as_markup(), parse_mode="html")


@router.callback_query(F.data == "confirm_deposit")
async def confirm_deposit(callback: CallbackQuery):
    amount = user_deposits.get(callback.from_user.id, {}).get("amount")
    if not amount:
        await callback.answer("❗ Խնդիր:")
        return

    payload = f"deposit-stars:{callback.from_user.id}:{amount}"
    prices = [LabeledPrice(label="Լիցքավորել բալանսը", amount=amount)]
    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Լիցքավորում",
        description=f"Լիցքավորել {amount} ⭐️",
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=prices
    )
    await callback.answer()


@router.pre_checkout_query()
async def process_pre_checkout_query(query: PreCheckoutQuery):
    try:
        prefix, user_id, amount = query.invoice_payload.split(":")
        valid = (
            prefix == "deposit-stars"
            and int(user_id) == query.from_user.id
            and int(amount) == query.total_amount
            and query.currency == "XTR"
        )
    except (ValueError, AttributeError):
        valid = False

    await query.answer(
        ok=valid,
        error_message=None if valid else "Վճարման տվյալները սխալ են։ Խնդրում ենք նորից փորձել։"
    )


@router.message(F.successful_payment)
async def process_invoice_payment(message: Message):
    user_id = message.from_user.id
    payment = message.successful_payment
    try:
        prefix, invoice_user_id, invoice_amount = payment.invoice_payload.split(":")
        stars = int(invoice_amount)
        valid = (
            prefix == "deposit-stars"
            and int(invoice_user_id) == user_id
            and stars == payment.total_amount
            and payment.currency == "XTR"
        )
    except (ValueError, AttributeError):
        valid = False

    if not valid:
        logging.error(
            "Received a successful payment with an invalid invoice payload for user %s",
            user_id
        )
        await message.answer("❗ Վճարումը չհաջողվեց ստուգել։ Կապ հաստատեք աջակցության հետ։")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        result = await db.execute(
            "INSERT OR IGNORE INTO processed_payments "
            "(payment_charge_id, user_id, stars, created_at) VALUES (?, ?, ?, ?)",
            (
                payment.telegram_payment_charge_id,
                user_id,
                stars,
                datetime.now().isoformat()
            )
        )
        if result.rowcount == 1:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                (user_id, message.from_user.username)
            )
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (stars, user_id)
            )
            await db.execute(
                "INSERT INTO balance_history "
                "(user_id, tx_type, amount, partner_desc, created_at) VALUES (?,?,?,?,?)",
                (user_id, "Invoice XTR", stars, f"{stars} ⭐️", datetime.now().isoformat())
            )
        await db.commit()

    if result.rowcount == 1:
        await message.answer(
            f"✅ Լիցքավորումը հաջողվեց! Ձեր բալանսը ավելացավ "
            f"{stars} <tg-emoji emoji-id='{star_emoji}'>⭐️</tg-emoji>",
            parse_mode="HTML"
        )
    else:
        await message.answer("✅ Այս վճարումն արդեն հաշվառված է։")


# ---------- НАЗАД В ГЛАВНОЕ МЕНЮ ----------
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer(
        "<tg-emoji emoji-id='5366574705937499149'>🔹</tg-emoji> Գլխավոր մենյու`",
        reply_markup=main_menu_kb(),
        parse_mode="html"
    )
    await callback.answer()
