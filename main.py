import asyncio
import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
from config import BOT_TOKEN
from db import init_db
from handlers import user, admin, common

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # --- Common Handlers ---
    app.add_handler(CommandHandler("start", common.start))
    app.add_handler(CommandHandler("help", common.help_cmd))
    app.add_handler(CommandHandler("menu", common.menu))
    
    # --- User Handlers ---
    app.add_handler(CallbackQueryHandler(user.handle_callback, pattern="^user:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, user.handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO, user.handle_video))
    app.add_handler(CommandHandler("pause", user.pause_user))
    app.add_handler(CommandHandler("resume", user.resume_user))
    app.add_handler(CommandHandler("status", user.status_user))

    # --- Admin Handlers ---
    app.add_handler(CallbackQueryHandler(admin.handle_callback, pattern="^admin:"))

    # --- Background Tasks ---
    app.job_queue.run_repeating(common.timeout_job, interval=180, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()