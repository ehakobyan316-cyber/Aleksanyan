import asyncio
from html import escape
import logging
import random

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "9166376948:AAHAxKiM2WGBK2fxYfufcvJ6DX8b62b0DSY"

BOT_API_PARSE_MODE = "HTML"
SEVEN_VALUE = 64  # 🎰 777 արժեքը
ADMIN_USERNAME = "@AleksanyanADM"

# 1 = Աստղեր (վանդակներով բացելու տարբերակ), 2 = NFT
GAME_MODE = 1

PREMIUM_EMOJI = {
    "slot": "5305559532947126301",
    "777": "6275805349626778419",
    "trophy": "5253742260054409879",
    "happy": "6309567129762926960",
    "gift": "5195100606250889609",
    "mail": "5424972470023104089",
    "fire": "5368324170671202286",
    "star": "5951810621887484519",
}


def format_premium_emoji(emoji_id: str, fallback: str, use_premium: bool = True) -> str:
    safe_fallback = escape(fallback)
    if not use_premium or not emoji_id:
        return safe_fallback
    return f'<tg-emoji emoji-id="{escape(emoji_id)}">{safe_fallback}</tg-emoji>'


def generate_win() -> int:
    roll = random.random()
    if roll <= 0.90:
        return random.choice(range(50, 65, 5))
    elif roll <= 0.99:
        return random.choice(range(60, 75, 5))
    elif roll <= 0.9900000005:
        return random.choice(range(70, 85, 5))
    else:
        return random.choice(range(80, 105, 5))


def build_stars_grid_keyboard(winner_id: int):
    kb = InlineKeyboardBuilder()
    for i in range(12):
        kb.button(text="🎁", callback_data=f"box_{i}:{winner_id}")
    kb.adjust(3, 3, 3, 3)
    return kb.as_markup()


def build_777_announcement(
    full_name: str,
    prize: str = "stars",
    use_premium: bool = True,
) -> str:
    name = escape(full_name or "Խաղացող")
    one_slot = format_premium_emoji(PREMIUM_EMOJI["slot"], "🎰", use_premium=use_premium)
    sevens = f"{one_slot}{one_slot}{one_slot}"
    star = format_premium_emoji(PREMIUM_EMOJI["star"], "⭐", use_premium=use_premium)
    gift = format_premium_emoji(PREMIUM_EMOJI["gift"], "🎁", use_premium=use_premium)
    mail = format_premium_emoji(PREMIUM_EMOJI["mail"], "✉️", use_premium=use_premium)
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥", use_premium=use_premium)
    happy = format_premium_emoji(PREMIUM_EMOJI["happy"], "🎉", use_premium=use_premium)

    if prize == "stars":
        return (
            f"{happy} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:</b>\n\n"
            f"{sevens} <b>{name}</b>, դուք շահեցիք {star} աստղեր:\n"
            f"{gift} Ընտրեք վանդակներից մեկը՝ ձեր աստղերը բացելու համար:\n"
            f"{mail} Մրցանակը ստանալու համար կապ հաստատեք {ADMIN_USERNAME} հետ:\n\n"
            f"{fire} Շնորհավորում ենք և մաղթում նոր հաղթանակներ:"
        )

    return (
        f"{happy} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:</b>\n\n"
        f"{sevens} <b>{name}</b>, դուք շահեցիք NFT:\n"
        f"{gift} Ձեր NFT մրցանակը պահպանված է:\n"
        f"{mail} Մրցանակը ստանալու համար կապ հաստատեք {ADMIN_USERNAME} հետ:\n\n"
        f"{fire} Շնորհավորում ենք և մաղթում նոր հաղթանակներ:"
    )


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=BOT_API_PARSE_MODE),
)
dp = Dispatcher()
router = Router()
dp.include_router(router)


async def is_bot_admin(chat_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
    except TelegramBadRequest:
        logging.exception("Չհաջողվեց ստուգել բոտի ադմինի կարգավիճակը %s չաթում", chat_id)
        return False

    return member.status in {
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR,
    }


@router.message(Command("testemoji"))
async def test_emoji_handler(message: Message) -> None:
    samples = {
        "happy": ("🎉", PREMIUM_EMOJI["happy"]),
        "star": ("⭐", PREMIUM_EMOJI["star"]),
        "gift": ("🎁", PREMIUM_EMOJI["gift"]),
        "mail": ("✉️", PREMIUM_EMOJI["mail"]),
        "fire": ("🔥", PREMIUM_EMOJI["fire"]),
        "trophy": ("🏆", PREMIUM_EMOJI["trophy"]),
        "slot": ("🎰", PREMIUM_EMOJI["slot"]),
    }
    ok_list = []
    bad_list = []

    for key, (fb, eid) in samples.items():
        test_html = f'<tg-emoji emoji-id="{escape(eid)}">{escape(fb)}</tg-emoji>'
        try:
            sent = await message.answer(test_html)
            await sent.delete()
            ok_list.append(key)
        except TelegramBadRequest as e:
            bad_list.append(f"{key} ({e.message})")

    await message.answer(
        f"✅ Աշխատող՝ {', '.join(ok_list) or 'չկա'}\n"
        f"❌ Սխալ տվող՝ {', '.join(bad_list) or 'չկա'}"
    )


@router.message(F.text == "/starsmode")
async def stars_mode_handler(message: Message) -> None:
    global GAME_MODE
    GAME_MODE = 1
    await message.answer("Միացվեց Աստղերի ռեժիմը (վանդակներով):")


@router.message(F.text == "/nftmode")
async def nft_mode_handler(message: Message) -> None:
    global GAME_MODE
    GAME_MODE = 2
    await message.answer("Միացվեց NFT ռեժիմը:")


@router.message(F.dice)
async def handle_777_slot(message: Message) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        return

    if not message.dice or message.dice.emoji != "🎰":
        return

    if message.dice.value != SEVEN_VALUE:
        return

    if not await is_bot_admin(message.chat.id):
        return

    user_id = message.from_user.id if message.from_user else 0
    full_name = message.from_user.full_name if message.from_user else "Խաղացող"
    prize = "stars" if GAME_MODE == 1 else "nft"
    reply_markup = build_stars_grid_keyboard(user_id) if prize == "stars" else None

    text = build_777_announcement(full_name=full_name, prize=prize, use_premium=True)
    try:
        await message.reply(text, reply_markup=reply_markup)
    except TelegramBadRequest as err:
        if "ENTITY_TEXT_INVALID" in str(err):
            logging.warning("ENTITY_TEXT_INVALID հաղորդագրության ժամանակ (%s): %s", prize, err)
            fallback_text = build_777_announcement(
                full_name=full_name,
                prize=prize,
                use_premium=False,
            )
            await message.reply(fallback_text, reply_markup=reply_markup)
        else:
            raise


@router.callback_query(F.data.startswith("box_"))
async def handle_star_box(call: CallbackQuery) -> None:
    if not call.data or not call.message:
        return

    data_part, winner_id_str = call.data.split(":", 1)
    if str(call.from_user.id) != winner_id_str:
        await call.answer("⛔ Միայն հաղթողը կարող է բացել վանդակը։", show_alert=True)
        return

    chosen_index = int(data_part.split("_", 1)[1])
    values = [generate_win() for _ in range(12)]
    won_stars = values[chosen_index]

    kb = InlineKeyboardBuilder()
    for i, val in enumerate(values):
        label = f"✅ {val}" if i == chosen_index else str(val)
        kb.button(text=label, callback_data="disabled")
    kb.adjust(3, 3, 3, 3)

    star = format_premium_emoji(PREMIUM_EMOJI["star"], "⭐", use_premium=True)
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥", use_premium=True)
    mail = format_premium_emoji(PREMIUM_EMOJI["mail"], "✉️", use_premium=True)
    trophy = format_premium_emoji(PREMIUM_EMOJI["trophy"], "🏆", use_premium=True)

    result_text = (
        f"{trophy} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ, {escape(call.from_user.first_name)}!</b>\n\n"
        f"{fire} Դուք բացեցիք վանդակը և շահեցիք <b>{won_stars}</b> {star} աստղ:\n"
        f"{mail} Մրցանակը ստանալու համար կապ հաստատեք {ADMIN_USERNAME} հետ:"
    )

    try:
        await call.message.edit_text(result_text, reply_markup=kb.as_markup())
    except TelegramBadRequest as err:
        if "ENTITY_TEXT_INVALID" in str(err):
            logging.warning("ENTITY_TEXT_INVALID վանդակը բացելիս: %s", err)
            plain_result = (
                f"🏆 <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ, {escape(call.from_user.first_name)}!</b>\n\n"
                f"🔥 Դուք բացեցիք վանդակը և շահեցիք <b>{won_stars}</b> ⭐ աստղ:\n"
                f"✉️ Մրցանակը ստանալու համար կապ հաստատեք {ADMIN_USERNAME} հետ:"
            )
            await call.message.edit_text(plain_result, reply_markup=kb.as_markup())
        else:
            raise
    await call.answer()


@router.callback_query(F.data == "disabled")
async def handle_disabled_button(call: CallbackQuery) -> None:
    await call.answer("Այս վանդակներն արդեն բացված են։", show_alert=False)


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Տեղադրեք նոր բոտի BOT_TOKEN-ը կոդի մեջ։")

    while True:
        try:
            await dp.start_polling(bot, polling_timeout=30)
        except asyncio.CancelledError:
            raise
        except Exception:
            logging.exception("Polling-ը ընդհատվեց, 3 վայրկյանից կփորձի վերագործարկվել...")
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())

