# Aleksanyan bots

The repository contains a Telegram bot with the shop and slot game integrated:

- `aleksanyan.py` — starts the bot and registers both the shop and slot-game menus.
- `shopstars.py` — contains the shop handlers and can also be run standalone.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set the bot token and run the integrated bot:

```powershell
$env:ALEKSANYAN_BOT_TOKEN = "your-bot-token"
python aleksanyan.py
```

To run only the shop as a separate bot instead:

```powershell
$env:SHOPSTARS_BOT_TOKEN = "your-ShopStars-token"
python shopstars.py
```

Do not put bot tokens in source code or commit them. Tokens previously present in
the source should be revoked and replaced through BotFather.
