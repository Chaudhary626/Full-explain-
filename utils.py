import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_IDS, PROOF_PATH, THUMB_PATH
import glob

def is_admin(uid):
    return int(uid) in ADMIN_IDS

def build_main_menu(user):
    kb = [
        [InlineKeyboardButton("🎬 Upload Video", callback_data="user:upload")],
        [InlineKeyboardButton("📂 My Videos", callback_data="user:myvideos")],
        [InlineKeyboardButton("✅ Ready for Task", callback_data="user:ready")],
        [InlineKeyboardButton("🎯 My Task", callback_data="user:mytask")],
        [InlineKeyboardButton("⏸ Pause", callback_data="user:pause")],
        [InlineKeyboardButton("▶ Resume", callback_data="user:resume")],
        [InlineKeyboardButton("📊 Status", callback_data="user:status")]
    ]
    if is_admin(user['id']):
        kb.append([InlineKeyboardButton("👮 Admin Panel", callback_data="admin:panel")])
    return InlineKeyboardMarkup(kb)

def build_upload_menu():
    kb = [
        [InlineKeyboardButton("Cancel", callback_data="user:upload_cancel")]
    ]
    return InlineKeyboardMarkup(kb)

def build_video_menu(video_id):
    kb = [
        [InlineKeyboardButton("❌ Remove Video", callback_data=f"user:removevideo:{video_id}")]
    ]
    return InlineKeyboardMarkup(kb)

def build_task_menu(task_id, proof_status, verify_status):
    kb = []
    if not proof_status:
        kb.append([InlineKeyboardButton("📤 Submit Proof", callback_data=f"user:submitproof:{task_id}")])
    if proof_status and not verify_status:
        kb.append([
            InlineKeyboardButton("✅ Approve", callback_data=f"user:review:{task_id}:approve"),
            InlineKeyboardButton("❌ Reject", callback_data=f"user:review:{task_id}:reject"),
            InlineKeyboardButton("🚩 Report", callback_data=f"user:review:{task_id}:report"),
        ])
    return InlineKeyboardMarkup(kb)

def build_admin_menu():
    kb = [
        [InlineKeyboardButton("👥 Users", callback_data="admin:users")],
        [InlineKeyboardButton("📝 Complaints", callback_data="admin:complaints")],
        [InlineKeyboardButton("⚠️ Strikes", callback_data="admin:strikes")],
        [InlineKeyboardButton("🔒 Ban/Unban", callback_data="admin:ban")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin:stats")],
    ]
    return InlineKeyboardMarkup(kb)

async def send_long_message(update, text, parse_mode="HTML"):
    chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode=parse_mode)

def cleanup_old_proofs():
    files = glob.glob(os.path.join(PROOF_PATH, "*.mp4"))
    for f in files:
        try:
            if (os.path.getmtime(f) + 7*24*3600) < os.path.getmtime(f):
                os.remove(f)
        except Exception:
            pass

def get_readable_time(dtstring):
    from datetime import datetime
    dt = datetime.fromisoformat(dtstring)
    return dt.strftime("%d %b %Y %H:%M")