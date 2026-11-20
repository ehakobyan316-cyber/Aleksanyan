import asyncio
from html import escape
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters import Command

# Տեղադրիր բոտի տոկենը այստեղ՝ չակերտների մեջ
BOT_TOKEN = "8226041722:AAHciTQ_7AiSApJ-YTnHtDgroMJqqo0GUTg"

# Ընտրիր մրցանակի տեսակը՝ "stars" կամ "nft"
DEFAULT_PRIZE = "stars"

# Պտտվելու դադարը (վայրկյան), որպեսզի 🎰 անիմացիան ավարտվի
SPIN_DELAY_SECONDS = 2.5

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


def format_premium_emoji(emoji_id: str, fallback: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{escape(fallback)}</tg-emoji>'


def build_777_announcement(full_name: str, prize: str = "stars") -> str:
    name = escape(full_name or "Խաղացող")
    trophy_777 = format_premium_emoji(PREMIUM_EMOJI["777"], "777")
    slot = format_premium_emoji(PREMIUM_EMOJI["slot"], "🎰")
    star = format_premium_emoji(PREMIUM_EMOJI["star"], "⭐")
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥")
    mail = format_premium_emoji(PREMIUM_EMOJI["mail"], "✉️")

    prize_text = f"{star} աստղեր" if prize == "stars" else "NFT"
    return (
        f"{slot}{slot}{slot} {trophy_777} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:</b>\n\n"
        f"<b>{name}</b>, դուք խաղի մեջ հաղթել եք 777 և շահել եք {prize_text}:\n"
        f"{fire} Մաղթում ենք նոր հաղթանակներ:\n"
        f'{mail} Մրցանակը ստանալու համար կապ հաստատեք <a href="https://t.me/Aleksanyan0001">@Aleksanyan0001</a> հետ:'
    )


def build_nft_777_announcement(full_name: Optional[str] = None) -> str:
    trophy = format_premium_emoji(PREMIUM_EMOJI["trophy"], "🎆")
    happy = format_premium_emoji(PREMIUM_EMOJI["happy"], "😃")
    slot = format_premium_emoji(PREMIUM_EMOJI["slot"], "🎰")
    gift = format_premium_emoji(PREMIUM_EMOJI["gift"], "🎁")
    mail = format_premium_emoji(PREMIUM_EMOJI["mail"], "✉️")
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥")

    user_line = f"<b>{escape(full_name)}</b>, դուք" if full_name else "Դուք"

    return (
        f"{trophy} <b>ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:</b>\n\n"
        f"{happy} {user_line} ստացաք {slot}{slot}{slot} և շահեցիք՝ <b>NFT</b>:\n"
        f"{gift} Ձեր NFT մրցանակը պահպանված է։\n"
        f'{mail} Մրցանակը ստանալու համար կապ հաստատեք <a href="https://t.me/Aleksanyan0001">@Aleksanyan0001</a> հետ։\n\n'
        f"{fire} Շնորհավորում ենք և մաղթում նոր հաղթանակներ։"
    )


logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    raise RuntimeError("Տեղադրիր բոտի տոկենը BOT_TOKEN փոփոխականի մեջ")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


@dp.message(Command("getid"))
async def get_custom_emoji_id(message: types.Message):
    if not message.reply_to_message or not message.reply_to_message.entities:
        await message.reply("Reply արա այն հաղորդագրությանը, որի մեջ կա Premium Emoji։")
        return

    found = []
    text = message.reply_to_message.text or message.reply_to_message.caption or ""
    for entity in message.reply_to_message.entities:
        if entity.type == "custom_emoji":
            emoji_char = text[entity.offset : entity.offset + entity.length]
            found.append(f"{emoji_char} → <code>{entity.custom_emoji_id}</code>")

    if found:
        await message.reply("Գտնված Premium Emoji ID-ներ.\n" + "\n".join(found))
    else:
        await message.reply("Այդ հաղորդագրության մեջ Premium Emoji չկա։")


@dp.message(F.chat.type.in_({"group", "supergroup"}), F.dice)
async def on_slot_777(message: types.Message):
    if not message.dice or message.dice.emoji != "🎰" or message.dice.value != 64:
        return

    member = await bot.get_chat_member(message.chat.id, bot.id)
    if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
        return

    if SPIN_DELAY_SECONDS > 0:
        await asyncio.sleep(SPIN_DELAY_SECONDS)

    full_name = message.from_user.full_name if message.from_user else "Խաղացող"
    if DEFAULT_PRIZE == "nft":
        announcement = build_nft_777_announcement(full_name=full_name)
    else:
        announcement = build_777_announcement(full_name=full_name, prize=DEFAULT_PRIZE)

    await message.reply(announcement)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
