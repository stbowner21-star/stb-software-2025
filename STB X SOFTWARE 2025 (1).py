import logging
import random
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USERS_FILE = "users.json"
SIGNAL_LOG_FILE = "signal_logs.json"
PREMIUM_USERS_FILE = "premium_users.json"
BANNED_USERS_FILE = "banned_users.json"

ADMIN_ID = 5470323876
LOGIN_USERNAME = "STB OWNER"
LOGIN_PASSWORD = "@shakwat33s"

USERNAME, PASSWORD = range(2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(list(registered_users), f)

def load_premium_users():
    if os.path.exists(PREMIUM_USERS_FILE):
        with open(PREMIUM_USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_premium_users():
    with open(PREMIUM_USERS_FILE, "w") as f:
        json.dump(list(premium_users), f)

def load_banned_users():
    if os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_banned_users():
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(list(banned_users), f)

def log_signal(user_id, user_name, signals_text):
    log_entry = {
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": datetime.now().isoformat(),
        "signals": signals_text
    }
    logs = []
    if os.path.exists(SIGNAL_LOG_FILE):
        with open(SIGNAL_LOG_FILE, "r") as f:
            logs = json.load(f)
    logs.append(log_entry)
    with open(SIGNAL_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

registered_users = load_users()
premium_users = load_premium_users()
banned_users = load_banned_users()

user_signal_count = defaultdict(lambda: {"count": 0, "date": datetime.now().date()})
DAILY_LIMIT = 1

def generate_signal():
    assets = [
        "DASH", "USDCOP", "SHIUSD","USDNGN","NZDJPY","BONK","USDBDT", "NZDCHF", "USDEGP", "BRLUSD", "BONK", "USDPKR","TRUMP", "TONUSD", "BTCUSD", "ZCASH", "APTOS", "BEAM", "GALA", "RIPPLE", "FLOKI", "SOLANA", "CHAINLINK", "AXIE", "COSMOS", "CARDANO"
    ]
    return f"{random.choice(assets)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id in registered_users:
        await update.message.reply_text("✅ You are already logged in.\nUse /signal to get signals.")
        return ConversationHandler.END
    await update.message.reply_text("🔐 Please enter your username:")
    return USERNAME

async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["username"] = update.message.text.strip()
    await update.message.reply_text("🔑 Now enter your password:")
    return PASSWORD

async def check_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    username = context.user_data.get("username")
    user_id = update.effective_user.id
    if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
        registered_users.add(user_id)
        save_users()
        await update.message.reply_text(f"✅ Login successful! Welcome {username}.\nUse /signal to get signals.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Invalid credentials. Try /start again.")
        return ConversationHandler.END

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id

    if user_id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return

    if user_id not in registered_users:
        await update.message.reply_text("🔒 Please log in first using /start.")
        return

    today = datetime.now().date()
    user_data = user_signal_count[user_id]

    if user_id not in premium_users:
        if user_data["date"] != today:
            user_data["date"] = today
            user_data["count"] = 0
        if user_data["count"] >= DAILY_LIMIT:
            await update.message.reply_text("⚠️ You've reached your daily free signal limit.\nUpgrade to Premium for unlimited access. Contact owner: @shakwat33s")
            return
        user_data["count"] += 1

    num_signals = random.randint(5, 10)
    current_time = datetime.now()
    signal_times = sorted([
        current_time + timedelta(minutes=random.randint(1, 60))
        for _ in range(num_signals)
    ])
    signals = "TIME ZONE UTC +6:00\nTIME : 1 MINUTE\n1 STEP MTG MAX\nBROKER: QUOTEX"
    for signal_time in signal_times:
        asset = generate_signal()
        direction = random.choice(["CALL", "PUT"])
        signals += f"\n{asset}-OTC  {signal_time.strftime('%H:%M')} - {direction}"
    signals += "\n⚙️  STB X SOFTWARE \nSIGNAL PROVIDER : STB\nSEND YOUR FEEDBACK :"
    log_signal(user_id, user.first_name, signals)
    await update.message.reply_text(signals)

# --- Admin functions ---

async def make_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to make users premium.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: /makepremium <user_id>")
        return
    try:
        target_id = int(context.args[0])
        premium_users.add(target_id)
        save_premium_users()
        await update.message.reply_text(f"✅ User {target_id} is now Premium.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def remove_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to remove premium.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: /removepremium <user_id>")
        return
    try:
        target_id = int(context.args[0])
        if target_id in premium_users:
            premium_users.remove(target_id)
            save_premium_users()
            await update.message.reply_text(f"🧾 User {target_id} is no longer Premium.")
        else:
            await update.message.reply_text(f"ℹ️ User {target_id} was not Premium.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to ban users.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: /ban <user_id>")
        return
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        save_banned_users()
        await update.message.reply_text(f"🚫 User {target_id} has been banned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to unban users.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: /unban <user_id>")
        return
    try:
        target_id = int(context.args[0])
        if target_id in banned_users:
            banned_users.remove(target_id)
            save_banned_users()
            await update.message.reply_text(f"✅ User {target_id} has been unbanned.")
        else:
            await update.message.reply_text(f"ℹ️ User {target_id} is not banned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def clear_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to clear logs.")
        return
    if os.path.exists(SIGNAL_LOG_FILE):
        os.remove(SIGNAL_LOG_FILE)
        await update.message.reply_text("✅ All logs have been cleared.")
    else:
        await update.message.reply_text("📭 No logs to clear.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    if not context.args:
        await update.message.reply_text("ℹ️ Please provide a message to broadcast. Example: /broadcast Hello users!")
        return
    message = " ".join(context.args)
    count = 0
    for uid in registered_users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 {message}")
            count += 1
        except Exception as e:
            logging.warning(f"Failed to send to {uid}: {e}")
    await update.message.reply_text(f"✅ Message sent to {count} users.")

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to view users.")
        return
    if not registered_users:
        await update.message.reply_text("📭 No users registered yet.")
        return
    user_list = "👥 Registered Users:\n"
    for uid in registered_users:
        try:
            user_obj = await context.bot.get_chat(uid)
            status = "Premium" if uid in premium_users else "Free"
            user_list += f"- {user_obj.first_name} (ID: {uid}) [{status}]\n"
        except:
            user_list += f"- Unknown User (ID: {uid})\n"
    await update.message.reply_text(user_list)

async def reset_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to reset users.")
        return
    registered_users.clear()
    save_users()
    await update.message.reply_text("🔄 All registered users have been reset. They must log in again using /start.")

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to view logs.")
        return
    if not os.path.exists(SIGNAL_LOG_FILE):
        await update.message.reply_text("📭 No logs found.")
        return
    with open(SIGNAL_LOG_FILE, "r") as f:
        logs = json.load(f)
    if not logs:
        await update.message.reply_text("📭 No logs found.")
        return
    for log in logs:
        log_text = (
            f"👤 {log['user_name']} (ID: {log['user_id']})\n"
            f"🕒 {log['timestamp']}\n"
            f"🧾 Signals:\n{log['signals']}"
        )
        try:
            await update.message.reply_text(log_text[:4000])
        except:
            continue

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"🆔 Your Telegram ID: {update.effective_user.id}")

async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to view user count.")
        return
    count = len(registered_users)
    await update.message.reply_text(f"👥 Total registered users: {count}")

# --- New commands requested by user ---

async def premium_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show how many premium users exist (admin only)."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to view premium user count.")
        return
    count = len(premium_users)
    if count == 0:
        await update.message.reply_text("💎 Currently, there are no Premium users.")
    else:
        await update.message.reply_text(f"💎 Total Premium users: {count}")

async def premium_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show a detailed list of premium users with Telegram name/username and ID.
    Admin only.
    """
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to view premium users.")
        return

    if not premium_users:
        await update.message.reply_text("💎 No Premium users found.")
        return

    premium_text = f"💎 Total Premium Users: {len(premium_users)}\n\n"
    for uid in premium_users:
        try:
            user_obj = await context.bot.get_chat(uid)
            # Prefer to show full name (first + last if available)
            full_name = " ".join(
                part for part in [getattr(user_obj, "first_name", ""), getattr(user_obj, "last_name", "")] if part
            ).strip()
            display_name = full_name if full_name else "—"
            username = f"@{user_obj.username}" if getattr(user_obj, "username", None) else "—"
            premium_text += f"👤 {display_name} ({username})\n🆔 {uid}\n\n"
        except Exception as e:
            # If bot can't fetch chat info (user blocked bot or error), still show ID
            premium_text += f"❓ Unknown User (ID: {uid})\n\n"

    # Respect Telegram message size limits by chunking if necessary
    if len(premium_text) > 4000:
        chunks = [premium_text[i:i + 4000] for i in range(0, len(premium_text), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(premium_text)

def main():
    TOKEN = "8142844054:AAFTCrdwhwEgcdqZARdZQTph9AFBFIM5I9w"
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_login)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)

    # user commands
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("myid", myid))

    # admin commands
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("clearlogs", clear_logs))
    app.add_handler(CommandHandler("makepremium", make_premium))
    app.add_handler(CommandHandler("removepremium", remove_premium))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("usercount", user_count))
    app.add_handler(CommandHandler("resetusers", reset_users))

    # new premium commands
    app.add_handler(CommandHandler("premiumcount", premium_count))
    app.add_handler(CommandHandler("premiumlist", premium_list))

    print("📡 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()