import json
import secrets
import os, re
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()]
)

# Replace this with your Telegram bot token
BOT_TOKEN = "8525801385:AAGdNm2DXTBkJa_ng6Eq3pGYeJ5LStJ6fQQ"

# Define file paths
LOGS_FOLDER = "/home/container/Database"
SESSION_FILE = "session_keys.json"

# Admin ID (replace with your actual Telegram user ID)
ADMIN_ID = 8066288821

# Ensure necessary folders exist
if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

import json
import os

def load_session_keys():
    path = "session_keys.json"
    
    # Kung walang file, gumawa ng bago
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
        return {}

    # Kung may file pero empty o sira, ayusin
    with open(path, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
        except json.JSONDecodeError:
            # Gumawa ulit ng valid file kung invalid JSON
            with open(path, "w") as f2:
                json.dump({}, f2)
            return {}


# Save session keys
def save_session_keys(session_keys):
    with open(SESSION_FILE, 'w') as file:
        json.dump(session_keys, file, indent=4)

# Notify admin of expired keys
async def notify_admin_of_expired_keys(context: ContextTypes.DEFAULT_TYPE) -> None:
    expired_keys = []
    for key, details in list(session_keys.items()):
        expiration_time = datetime.fromisoformat(details["expires_at"])
        if datetime.now() > expiration_time:
            expired_keys.append(key)
            del session_keys[key]

    if expired_keys:
        save_session_keys(session_keys)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 Expired keys removed: {', '.join(expired_keys)}")
        logging.info(f"Expired keys removed: {expired_keys}")

# Load session keys on startup
session_keys = load_session_keys()
logging.info("Session keys loaded successfully.")

# ====================== START COMMAND ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"
    full_name = f"{user.first_name} {user.last_name}".strip() if user.last_name else user.first_name
    language = user.language_code if user.language_code else "Unknown"

    logging.debug(f"User {user_id} started the bot.")

    admin_message = (
        f"🔔 **New User Started the Bot**\n\n"
        f"👤 **Name:** {full_name}\n"
        f"🔹 **Username:** {username}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🌍 **Language:** {language}\n"
        f"📅 **Joined at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")

    await notify_admin_of_expired_keys(context)

    if str(user_id) in session_keys:
        expiration_time = datetime.fromisoformat(session_keys[str(user_id)]["expires_at"])
        if datetime.now() < expiration_time:
            await update.message.reply_text("👋 Welcome back! Use /search <keyword> <lines> to search logs.")
            return

    await update.message.reply_text("👋 Welcome! Please redeem a key using /redeem <key>.")

# ====================== REDEEM COMMAND ======================
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("❌ Provide a key. Usage: /redeem <key>")
        return

    key = context.args[0]
    user = update.message.from_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else "No Username"
    full_name = f"{user.first_name} {user.last_name}".strip() if user.last_name else user.first_name
    language = user.language_code if user.language_code else "Unknown"

    await notify_admin_of_expired_keys(context)

    if key not in session_keys:
        await update.message.reply_text("❌ Invalid key!")
        return

    expiration_time = datetime.fromisoformat(session_keys[key]["expires_at"])
    if datetime.now() > expiration_time:
        del session_keys[key]
        save_session_keys(session_keys)
        await update.message.reply_text("❌ This key has expired!")
        return

    session_keys[user_id] = session_keys.pop(key)
    save_session_keys(session_keys)

    logging.info(f"User {user_id} redeemed key {key}.")

    await update.message.reply_text("✅ Key redeemed successfully!")

    admin_message = (
        f"🔑 **Key Redeemed**\n\n"
        f"👤 **Name:** {full_name}\n"
        f"🔹 **Username:** {username}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🌍 **Language:** {language}\n"
        f"🔑 **Used Key:** `{key}`\n"
        f"⏳ **Expires At:** {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")

# ====================== GETKEY COMMAND ======================
async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /getkey <duration> <unit>")
        return

    try:
        duration = int(context.args[0])
        unit = context.args[1].lower()

        current_time = datetime.now()
        if unit == "days":
            expiration_time = current_time + timedelta(days=duration)
        elif unit == "hours":
            expiration_time = current_time + timedelta(hours=duration)
        elif unit == "minutes":
            expiration_time = current_time + timedelta(minutes=duration)
        elif unit == "seconds":
            expiration_time = current_time + timedelta(seconds=duration)
        else:
            await update.message.reply_text("❌ Invalid unit. Use 'days', 'hours', 'minutes', or 'seconds'.")
            return

    except ValueError:
        await update.message.reply_text("❌ Provide a valid duration.")
        return

    key = secrets.token_urlsafe(16)
    session_keys[key] = {"expires_at": expiration_time.isoformat(), "duration": f"{duration} {unit}"}
    save_session_keys(session_keys)

    logging.info(f"Admin generated key: {key} (Expires: {expiration_time})")

    # Improved formatting for key message
    message = (
        f"🔑 *KEY GENERATED*\n"
        f"────────────────────────\n"
        f"{key}\n\n"
        f"⏳ Duration: {duration} {unit}\n"
        f"📅 Expires: {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"────────────────────────"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# ====================== HELP COMMAND ======================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 *Bot Commands Guide*\n\n"
        "🔹 /start - Start the bot and check your session status.\n"
        "🔹 /redeem <key> - Redeem a key to activate your session.\n"
        "🔹 /getkey <duration> <unit> - *Admin only:* Generate a new key (units: days, hours, minutes, seconds).\n"
        "🔹 /search <keyword> <lines> - Search logs for a keyword, returns a `.txt` file with results.\n"
        "🔹 /help - Show this help message.\n\n"
        "💡 *Example:* `/search bitcoin 10` will return the first 10 matching lines for 'bitcoin'."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ====================== SEARCH COMMAND ======================
user_search_history = {}

# Regex patterns for URL removal and prefix cleaning
url_pattern = re.compile(
    r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}'
    r'\.[a-zA-Z0-9()]{1,6}\b'
    r'[-a-zA-Z0-9()@:%_\+.~#?&//=]*'
)
pattern_to_remove = re.compile(r'^[^:]+:')

async def search_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.chat.id)
    logging.debug(f"User {user_id} initiated a search.")

    if user_id not in session_keys:
        await update.message.reply_text("❌ Redeem a key first. Use /redeem <key>")
        return

    expiration_time = datetime.fromisoformat(session_keys[user_id]["expires_at"])
    if datetime.now() > expiration_time:
        duration = session_keys[user_id]["duration"]
        del session_keys[user_id]
        save_session_keys(session_keys)
        await update.message.reply_text(f"❌ Your {duration} key has expired.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /search <keyword> <lines>")
        return

    keyword = context.args[0].lower()
    try:
        line_limit = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ The <lines> argument must be a valid integer.")
        return

    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=f"remove_url:yes:{keyword}:{line_limit}"),
         InlineKeyboardButton("No", callback_data=f"remove_url:no:{keyword}:{line_limit}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Do you want to remove URLs from the results?", reply_markup=reply_markup)

async def handle_url_removal_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    choice, keyword, line_limit = query.data.split(':')[1:]
    line_limit = int(line_limit)
    user_id = str(query.message.chat.id)

    remove_urls = choice == "yes"

    if user_id not in user_search_history:
        user_search_history[user_id] = {}
    if keyword not in user_search_history[user_id]:
        user_search_history[user_id][keyword] = set()

    previous_results = user_search_history[user_id][keyword]
    results = set()
    txt_files = [f for f in os.listdir(LOGS_FOLDER) if f.endswith(".txt")]

    async def countdown(context: ContextTypes.DEFAULT_TYPE, seconds: int):
        message = await context.bot.send_message(chat_id=query.message.chat.id, text=f"Searching logs... {seconds} seconds remaining.")
        for i in range(seconds, 0, -1):
            await asyncio.sleep(1)
            await context.bot.edit_message_text(chat_id=query.message.chat.id, message_id=message.message_id, text=f"Searching logs... {i} seconds remaining.")
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=message.message_id)

    countdown_task = asyncio.create_task(countdown(context, 10))

    for file_name in txt_files:
        file_path = os.path.join(LOGS_FOLDER, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if keyword in line.lower():
                        cleaned_line = line.strip()
                        if remove_urls:
                            cleaned_line = re.sub(url_pattern, '', cleaned_line).strip()
                        cleaned_line = re.sub(pattern_to_remove, '', cleaned_line).strip()
                        cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()
                        if cleaned_line and file_name not in cleaned_line and cleaned_line not in previous_results:
                            results.add(cleaned_line)
                    if len(results) >= line_limit:
                        break
            if len(results) >= line_limit:
                break
        except Exception as e:
            logging.error(f"Error reading {file_name}: {e}")
            await query.message.reply_text(f"❌ Error reading {file_name}: {e}")
            return

    countdown_task.cancel()

    if not results:
        logging.info(f"No new results found for {keyword}.")
        await query.message.reply_text(f"✅ No new results found for '{keyword}', you've seen all matches.")
        return

    user_search_history[user_id][keyword].update(results)

    result_filename = f"{keyword}_zach_results.txt"
    with open(result_filename, "w", encoding="utf-8") as result_file:
        result_file.write("\n".join(results))

    logging.info(f"New search results sent for '{keyword}'.")
    await query.message.reply_document(open(result_filename, "rb"), filename=result_filename)
    os.remove(result_filename)

# ====================== MAIN FUNCTION ======================
def main() -> None:
    logging.info("Starting bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("getkey", get_key))
    application.add_handler(CommandHandler("search", search_logs))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_url_removal_choice, pattern='^remove_url:'))

    logging.info("Bot is now running.")
    application.run_polling()

if __name__ == "__main__":
    main()
