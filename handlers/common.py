from telegram import Update
from telegram.ext import ContextTypes
from db import add_user, get_user
from utils import build_main_menu, send_long_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)
    await update.message.reply_text(
        f"👋 Namaste {user.mention_html()}! Yeh bot YouTube mutual engagement ke liye hai.\n"
        "Koi bhi galat kaam, cheating ya inactivity par penalty hai.\n\n"
        "Menu se continue karein 👇",
        reply_markup=build_main_menu(get_user(user.id)), parse_mode="HTML"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_long_message(
        update, 
        "📋 <b>Bot Rules & Flow:</b>\n"
        "1️⃣ Apni YouTube video upload karein (title, thumbnail, link, duration)\n"
        "2️⃣ Jab ready ho, 'Ready' dabaye. Pairing ke baad aapko kisi ki video milegi dekhne ko.\n"
        "3️⃣ Video instructions ke hisab se dekhein. Screen record karein poora process.\n"
        "4️⃣ Proof upload karein. Pair ka proof approve/reject bhi karein.\n"
        "5️⃣ Galat/fake proof ya cheating par 'Report to Admin' karein.\n"
        "6️⃣ Agar pair inactive/delay karta hai, system aapko aage le jayega, cheater ko warning/strike.\n"
        "7️⃣ /pause se break le sakte hain (pending task na ho toh).\n"
        "8️⃣ /status se apni progress dekhein.\n"
        "⚠️ 3 strike = ban, admin ke pass full control hai."
        "\n\nAapka experience fair aur transparent rahega! 🎯", parse_mode="HTML"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)
    await update.message.reply_text(
        "👇 Main Menu", reply_markup=build_main_menu(get_user(user.id))
    )

# --- Background Timeout/Cleanup Job ---
from db import get_pending_tasks_timeout, set_task_status, admin_strike_user
from utils import cleanup_old_proofs
from datetime import datetime, timedelta

async def timeout_job(app):
    while True:
        await asyncio.sleep(180)
        timeouts = get_pending_tasks_timeout()
        for task in timeouts:
            task_id, user_a, user_b, proof_a, proof_b, verify_a, verify_b, created = task
            now = datetime.now()
            created_dt = datetime.fromisoformat(created)
            timeout_limit = timedelta(hours=2)
            if proof_a and not verify_b and (now - created_dt) > timeout_limit:
                admin_strike_user(user_b)
                set_task_status(task_id, f"auto_a_eligible")
            if proof_b and not verify_a and (now - created_dt) > timeout_limit:
                admin_strike_user(user_a)
                set_task_status(task_id, f"auto_b_eligible")
        cleanup_old_proofs()