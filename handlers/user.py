from telegram import Update, InputFile
from telegram.ext import ContextTypes
from db import (
    add_user, get_user, get_user_active_video_count, add_video, get_videos_by_user, remove_video,
    get_ready_users, create_task_pair, get_task_for_user, submit_proof, verify_proof, get_video_by_id, get_task_by_id,
    set_user_paused, set_user_active, add_complaint, get_user_strikes, get_user_ban_status, get_user_pause_status, get_user_tasks
)
from utils import build_main_menu, build_upload_menu, build_video_menu, build_task_menu, send_long_message, get_readable_time
import os
from datetime import datetime

# --- Callback Handler ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(":")
    action = data[1]
    user = query.from_user

    if action == "upload":
        await query.message.reply_text(
            "🎬 <b>Step 1/4</b>\nSend your YouTube video <b>title</b>:", parse_mode="HTML"
        )
        context.user_data['upload_step'] = 1
        await query.answer()
    elif action == "upload_cancel":
        context.user_data.clear()
        await query.message.reply_text("❌ Upload cancelled.", reply_markup=build_main_menu(get_user(user.id)))
        await query.answer()
    elif action == "myvideos":
        await my_videos(update, context)
        await query.answer()
    elif action == "removevideo":
        video_id = int(data[2])
        video = get_video_by_id(video_id)
        if video and video['user_id'] == user.id:
            remove_video(video_id)
            await query.answer("✅ Video removed.", show_alert=True)
            await query.edit_message_caption("❌ Video removed.")
        else:
            await query.answer("Not allowed.", show_alert=True)
    elif action == "pause":
        await pause_user(update, context)
        await query.answer()
    elif action == "resume":
        await resume_user(update, context)
        await query.answer()
    elif action == "status":
        await status_user(update, context)
        await query.answer()
    elif action == "ready":
        await ready_for_task(update, context)
        await query.answer()
    elif action == "mytask":
        await my_task(update, context)
        await query.answer()
    elif action == "submitproof":
        task_id = int(data[2])
        context.user_data['submitproof_task_id'] = task_id
        await query.message.reply_text("📤 Send your screen-recording proof (video file):")
        context.user_data['upload_step'] = "proof"
        await query.answer()
    elif action == "review":
        task_id = int(data[2])
        review_action = data[3]
        await proof_review_handler(update, context, task_id, review_action)
        await query.answer()
    else:
        await query.answer("Unknown action.", show_alert=True)

# --- Text Handler ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.user_data.get('upload_step') == 1:
        context.user_data['video_title'] = update.message.text.strip()
        context.user_data['upload_step'] = 2
        await update.message.reply_text(
            "🖼 <b>Step 2/4</b>\nSend your video <b>thumbnail</b> (as photo):", parse_mode="HTML"
        )
    elif context.user_data.get('upload_step') == 3:
        link = update.message.text.strip()
        if link.lower() == "skip":
            link = ""
        context.user_data['video_link'] = link
        context.user_data['upload_step'] = 4
        await update.message.reply_text(
            "⏱ <b>Step 4/4</b>\nSend video <b>duration in seconds</b> (max 300):", parse_mode="HTML"
        )
    elif context.user_data.get('upload_step') == 4:
        try:
            duration = int(update.message.text.strip())
            if duration < 30 or duration > 300:
                raise ValueError
            context.user_data['video_duration'] = duration
        except Exception:
            await update.message.reply_text("❗Enter valid duration (30-300 seconds).")
            return
        add_video(
            user.id,
            context.user_data['video_title'],
            context.user_data.get('video_link', ""),
            context.user_data['video_thumb'],
            context.user_data['video_duration']
        )
        context.user_data.clear()
        await update.message.reply_text(
            "✅ Video uploaded! Check your active videos in menu.",
            reply_markup=build_main_menu(get_user(user.id))
        )
    elif context.user_data.get('upload_step') == "proof":
        await update.message.reply_text("❗Please send a video file as proof.")
    else:
        await update.message.reply_text("❓ Use the menu buttons for actions.", reply_markup=build_main_menu(get_user(user.id)))

# --- Photo Handler for Thumbnail ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('upload_step') == 2:
        file = await update.message.photo[-1].get_file()
        file_path = os.path.join("thumbs/", f"{update.effective_user.id}_{datetime.now().timestamp()}.jpg")
        await file.download_to_drive(file_path)
        context.user_data['video_thumb'] = file_path
        context.user_data['upload_step'] = 3
        await update.message.reply_text(
            "🔗 <b>Step 3/4</b>\nSend your YouTube video <b>link</b> (or type 'skip'):", parse_mode="HTML"
        )
    else:
        await update.message.reply_text("❓ Not expecting a photo.")

# --- Video Handler for Proof Submission ---
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.user_data.get('upload_step') == "proof":
        task_id = context.user_data.get('submitproof_task_id')
        file = await update.message.video.get_file()
        file_path = os.path.join("proofs/", f"{user.id}_{task_id}_{datetime.now().timestamp()}.mp4")
        await file.download_to_drive(file_path)
        submit_proof(task_id, user.id, file_path)
        context.user_data.clear()
        await update.message.reply_text("✅ Proof uploaded! Waiting for partner's review.")
    else:
        await update.message.reply_text("❓ Not expecting a video.")

# --- My Videos ---
async def my_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    videos = get_videos_by_user(user.id)
    if not videos:
        await update.message.reply_text("❌ No active videos found.")
        return
    for v in videos:
        msg = f"🎬 <b>{v['title']}</b>\n"
        if v['yt_link']:
            msg += f"🔗 {v['yt_link']}\n"
        msg += f"⏱ {v['duration']} sec"
        kb = build_video_menu(v['id'])
        await update.message.reply_photo(
            InputFile(v['thumb']), caption=msg, parse_mode="HTML", reply_markup=kb
        )

# --- Pause/Resume/Status ---
async def pause_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    set_user_paused(user.id)
    await update.message.reply_text("⏸ You are now paused. Use /resume to activate.", reply_markup=build_main_menu(get_user(user.id)))

async def resume_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    set_user_active(user.id)
    await update.message.reply_text("▶️ You are now active!", reply_markup=build_main_menu(get_user(user.id)))

async def status_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    strikes = get_user_strikes(user.id)
    banned = get_user_ban_status(user.id)
    paused = get_user_pause_status(user.id)
    tasks = get_user_tasks(user.id)
    msg = f"👤 <b>Status for {user.mention_html()}</b>\n"
    msg += f"Strikes: <b>{strikes}</b>\n"
    msg += f"Banned: <b>{'Yes' if banned else 'No'}</b>\n"
    msg += f"Paused: <b>{'Yes' if paused else 'No'}</b>\n"
    msg += f"Total Tasks: <b>{len(tasks)}</b>\n"
    await update.message.reply_text(msg, parse_mode="HTML")

# --- Ready for Task / Pairing ---
async def ready_for_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)
    paired, partner, task_id = create_task_pair(user.id)
    if paired:
        partner_user = get_user(partner)
        await update.message.reply_text(
            f"🤝 Paired with <b>{partner_user['username']}</b>!\n"
            "Check your assigned video in menu.", parse_mode="HTML"
        )
    else:
        await update.message.reply_text("⏳ Waiting for another user...")

# --- My Task / Assigned Video Details ---
async def my_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    task = get_task_for_user(user.id)
    if not task:
        await update.message.reply_text("❌ No current task. Use 'Ready' in menu.")
        return
    if user.id == task['user_a']:
        partner_id = task['user_b']
        assigned_video_id = task['video_b_id']
        proof_status = task['proof_a']
        verify_status = task['verify_a']
    else:
        partner_id = task['user_a']
        assigned_video_id = task['video_a_id']
        proof_status = task['proof_b']
        verify_status = task['verify_b']
    video = get_video_by_id(assigned_video_id)
    partner = get_user(partner_id)
    msg = (f"🎯 <b>Your Task</b>\n"
           f"You must watch <b>{partner['username']}</b>'s video:\n"
           f"🎬 <b>{video['title']}</b>\n"
           f"Duration: <b>{video['duration']} sec</b>\n")
    if video['yt_link']:
        msg += f"🔗 {video['yt_link']}\n"
    msg += "👇 Full instructions below:\n"
    msg += "1️⃣ Play video on YouTube\n2️⃣ Like, Comment, Subscribe\n3️⃣ Screen record full process\n4️⃣ Upload proof below 👇"
    kb = build_task_menu(task['id'], proof_status, verify_status)
    await update.message.reply_photo(
        InputFile(video['thumb']), caption=msg, parse_mode="HTML", reply_markup=kb
    )

# --- Approve/Reject/Report Proof ---
async def proof_review_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, task_id, action):
    task = get_task_by_id(task_id)
    user = update.effective_user
    if user.id not in [task['user_a'], task['user_b']]:
        await update.callback_query.answer("Not allowed.", show_alert=True)
        return
    if user.id == task['user_a']:
        reviewee = task['user_b']
        proof_file = task['proof_b']
    else:
        reviewee = task['user_a']
        proof_file = task['proof_a']
    if not proof_file:
        await update.callback_query.answer("No proof to review.", show_alert=True)
        return
    if action == "approve":
        verify_proof(task_id, user.id, "approved")
        await update.callback_query.answer("✅ Approved!", show_alert=True)
        await update.callback_query.edit_message_caption("✅ Proof approved.")
    elif action == "reject":
        verify_proof(task_id, user.id, "rejected")
        await update.callback_query.answer("❌ Rejected.", show_alert=True)
        await update.callback_query.edit_message_caption("❌ Proof rejected. Report if cheating.")
    elif action == "report":
        await update.callback_query.message.reply_text("🚩 Type reason for reporting:")
        context.user_data['report_task_id'] = task_id

# --- Report Reason (text) ---
async def handle_text_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    task_id = context.user_data.get('report_task_id')
    if not task_id:
        return
    reason = update.message.text.strip()
    task = get_task_by_id(task_id)
    if user.id == task['user_a']:
        accused = task['user_b']
        proof_file = task['proof_b']
    else:
        accused = task['user_a']
        proof_file = task['proof_a']
    add_complaint(user.id, accused, task_id, reason, proof_file)
    context.user_data.pop('report_task_id', None)
    await update.message.reply_text("🚩 Complaint submitted to admin.")