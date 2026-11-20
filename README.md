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

In a group where the bot is an administrator, a group administrator can set
that group's custom 777-win announcement with `/setwinner <text>`. Premium
custom emoji in the command are preserved; `{name}` is replaced with the
winner's name. The setting is stored separately for each group.

Do not put bot tokens in source code or commit them. Tokens previously present in
the source should be revoked and replaced through BotFather.
