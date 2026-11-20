import asyncio
from html import escape
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters import Command

BOT_TOKEN = "8996867611:AAG4zmTRRaQ3NcRsVqhOjfO3EecnV2gpFuk"
DEFAULT_PRIZE = "stars"  # "stars" կամ "nft"
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


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
        f"<b>{name}
    
