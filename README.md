# Mutual YouTube Engagement Telegram Bot

A production-ready, modular Telegram bot for fair mutual YouTube engagement with anti-cheat, stylish UI, and full admin controls.

## Folder Structure

```
/main.py
/db.py
/handlers/
  user.py
  admin.py
  common.py
/utils.py
/config.py
/requirements.txt
/.env
/README.md
```

## Features

- Pairwise video exchange (mutual proof verification)
- Anti-cheat: warnings/strikes, inactivity/cheating detection
- Stylish button-based UI
- Full admin panel: strikes, ban/unban, complaints, logs
- Pause/resume, user status, task logs
- Cross-platform (Termux, Heroku, Render, etc.)
- SQLite data storage

## Setup

1. **Clone repo & install requirements:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Configure .env:**
    ```
    BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    ADMIN_IDS=YourTelegramID,AnotherID
    DB_PATH=bot.db
    PROOF_PATH=proofs/
    THUMB_PATH=thumbs/
    ```

3. **Run bot:**
    ```sh
    python main.py
    ```

---

## Deployment

- Works on Termux, Heroku, Render, etc. No OS-specific code.
- Use `/start` to begin, use menu buttons for all actions.
- Admin panel is button-based and safe.

---

## License

MIT