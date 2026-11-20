import asyncio
from html import escape
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)

# Տեղադրիր քո ՆՈՐ բոտի տոկենը չակերտների մեջ
BOT_TOKEN = "8996867611:AAFwVhOeguOMQwWw6VswjRTz3SUZB391y28"

BOT_API_PARSE_MODE = "HTML"
SEVEN_VALUE = 64  # 🎰 777 արժեքը

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


def build_777_announcement(
    full_name: str,
    prize: str = "stars",
    use_premium: bool = True,
) -> str:
    name = escape(full_name or "Խաղացող")
    # Ուշադրություն. <tg-emoji>-ի ներսում ավելի ապահով է 1 էմոջի դնել (օրինակ՝ 🏆 կամ 🎰)
    trophy_777 = format_premium_emoji(PREMIUM_EMOJI["777"], "🏆", use_premium=use_premium)
    slot = format_premium_emoji(PREMIUM_EMOJI["slot"], "🎰", use_premium=use_premium)
    star = format_premium_emoji(PREMIUM_EMOJI["star"], "⭐", use_premium=use_premium)
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥", use_premium=use_premium)
    mail = format_premium_emoji(PREMIUM_EMOJI["mail"], "✉️", use_premium=use_premium)
    prize_text = f"{star} աստղեր" if prize == "stars" else "NFT"

    return (
        f"{slot}{slot}{slot} {trophy_777} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:</b>\n\n"
        f"<b>{name}</b>, դուք ֆռցրիք 777 և շահեցիք {prize_text}։\n\n"
        f"{fire} Շնորհավորում ենք և մաղթում նոր հաղթանակներ։\n"
        f"{mail} Մրցանակի համար կապ հաստատեք ադմինի հետ։"
    )


def build_nft_777_announcement(full_name: str = "Խաղացող", use_premium: bool = True) -> str:
    return build_777_announcement(full_name, "nft", use_premium=use_premium)


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

    full_name = message.from_user.full_name if message.from_user else "Խաղացող"
    text = build_777_announcement(full_name=full_name, prize="stars", use_premium=True)

    try:
        await message.reply(text, parse_mode=BOT_API_PARSE_MODE)
    except TelegramBadRequest as err:
        if "ENTITY_TEXT_INVALID" in str(err):
            logging.warning("ENTITY_TEXT_INVALID պրեմիում էմոջիի ժամանակ, ուղարկում եմ պահուստային տարբերակը")
            fallback_text = build_777_announcement(
                full_name=full_name,
                prize="stars",
                use_premium=False,
            )
            await message.reply(fallback_text, parse_mode=BOT_API_PARSE_MODE)
        else:
            raise


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Տեղադրեք նոր բոտի BOT_TOKEN-ը կոդի մեջ։")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())