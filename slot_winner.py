from html import escape


# Telegram Bot API sendMessage / sendDice reply text formatting
BOT_API_PARSE_MODE = "HTML"

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


def build_777_announcement(full_name: str, prize: str) -> str:
    name = escape(full_name)
    trophy = format_premium_emoji(PREMIUM_EMOJI["777"], "777")
    slot = format_premium_emoji(PREMIUM_EMOJI["slot"], "🎰")
    star = format_premium_emoji(PREMIUM_EMOJI["star"], "⭐")
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥")

    prize_text = f"{star} աստղեր" if prize == "stars" else "NFT"
    return (
        f"{slot}{slot}{slot} {trophy} ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
        f"{name}, դուք խաղի մեջ հաղթել եք 777 և շահել եք {prize_text}:\n"
        f"{fire} Մաղթում ենք նոր հաղթանակներ:\n"
        "✉️ Մրցանակը ստանալու համար կապ հաստատեք @Aleksanyan0001 հետ:"
    )


def build_nft_777_announcement() -> str:
    trophy = format_premium_emoji(PREMIUM_EMOJI["trophy"], "🎆")
    happy = format_premium_emoji(PREMIUM_EMOJI["happy"], "😃")
    slot = format_premium_emoji(PREMIUM_EMOJI["slot"], "🎰")
    gift = format_premium_emoji(PREMIUM_EMOJI["gift"], "🎁")
    mail = format_premium_emoji(PREMIUM_EMOJI["mail"], "✉️")
    fire = format_premium_emoji(PREMIUM_EMOJI["fire"], "🔥")

    return (
        f"{trophy} ՇՆՈՐՀԱՎՈՐՈՒՄ ԵՆՔ:\n\n"
        f"{happy} Դուք ստացաք {slot}{slot}{slot} և շահեցիք՝ NFT:\n"
        f"{gift} Ձեր NFT մրցանակը պահպանված է։\n"
        f"{mail} Մրցանակը ստանալու համար կապ հաստատեք "
        "<a href=\"https://t.me/Aleksanyan0001\">@Aleksanyan0001</a> հետ։\n\n"
        f"{fire} Շնորհավորում ենք և մաղթում նոր հաղթանակներ։"
    )
