from telegram import Update
from telegram.ext import ContextTypes
from db import get_admin_stats, get_complaints, get_all_users, admin_ban_user, admin_strike_user, admin_unban_user, admin_remove_strike
from utils import is_admin, build_admin_menu

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(":")
    action = data[1]
    user = query.from_user

    if not is_admin(user.id):
        await query.answer("Admin only.", show_alert=True)
        return

    if action == "panel":
        stats = get_admin_stats()
        await query.message.reply_text(
            f"👮 <b>Admin Panel</b>\n"
            f"Users: {stats['users']}\n"
            f"Active Tasks: {stats['active_tasks']}\n"
            f"Pending Complaints: {stats['complaints']}\n"
            f"Strikes Given: {stats['strikes']}\n"
            f"Banned Users: {stats['banned']}\n",
            parse_mode="HTML", reply_markup=build_admin_menu()
        )
        await query.answer()
    elif action == "users":
        users = get_all_users()
        msg = "👥 <b>User List</b>\n"
        for u in users:
            msg += f"ID: <code>{u[0]}</code> | @{u[1]} | Strikes: {u[2]} | Banned: {u[3]} | Paused: {u[4]}\n"
        await query.message.reply_text(msg, parse_mode="HTML")
        await query.answer()
    elif action == "complaints":
        complaints = get_complaints()
        if not complaints:
            await query.message.reply_text("No pending complaints.")
        else:
            msg = "📝 <b>Complaints Pending</b>\n"
            for c in complaints:
                msg += (f"ID: {c[0]} | From: <code>{c[1]}</code> | Against: <code>{c[2]}</code> | "
                        f"Task: {c[3]} | Reason: {c[4]}\n")
            await query.message.reply_text(msg, parse_mode="HTML")
        await query.answer()
    elif action == "ban":
        await query.message.reply_text("To ban/unban, use ban/unban buttons in user list (to be implemented).")
        await query.answer()
    elif action == "strikes":
        await query.message.reply_text("To strike/remove strike, use strike/remove buttons in user list (to be implemented).")
        await query.answer()
    elif action == "stats":
        stats = get_admin_stats()
        await query.message.reply_text(
            f"📊 <b>Stats</b>\n"
            f"Users: {stats['users']}\n"
            f"Active Tasks: {stats['active_tasks']}\n"
            f"Pending Complaints: {stats['complaints']}\n"
            f"Strikes Given: {stats['strikes']}\n"
            f"Banned Users: {stats['banned']}\n",
            parse_mode="HTML"
        )
        await query.answer()
    else:
        await query.answer("Unknown admin action.", show_alert=True)