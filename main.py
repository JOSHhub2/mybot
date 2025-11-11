import os
import json
import random
import asyncio
import hashlib
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# === CONFIGURATION ===
CONFIG = {
    "TOKEN": "8314834676:AAELNYstDs3N717JwjCxZXo8JIIiMkRnbSI",
    "ADMIN_ID": 8210638636,  # Replace with your admin ID
    "KEYS_FILE": "keys.json",
    "DATABASE_FILES": ["database/accounts1.txt", "database/accounts2.txt"],  # Multiple database files
    "USED_ACCOUNTS_FILE": "database/used_accounts.txt",
    "LINES_TO_SEND": 1000,
    "MAX_DAILY_GENERATIONS":999,  # Limit per user per day
    "BACKUP_FOLDER": "backups",
    "AUTO_BACKUP_INTERVAL": 500,  # 1 hour in seconds
    "ANTI_ABUSE_LIMIT": 999,  # Max requests per minute
    "DOMAINS": {
        "spotify": {"emoji": "🎵", "description": "Premium Spotify accounts"},
        "netflix": {"emoji": "🎬", "description": "Netflix premium subscriptions"},
        "discord": {"emoji": "💬", "description": "Discord Nitro accounts"},
        "steam": {"emoji": "🎮", "description": "Steam game accounts"},
        "origin": {"emoji": "🕹️", "description": "Origin game accounts"},
        "roblox": {"emoji": "👾", "description": "Roblox premium accounts"},
        "garena": {"emoji": "🌐", "description": "Garena game accounts"},
        "minecraft": {"emoji": "⛏️", "description": "Minecraft premium accounts"},
        "crunchyroll": {"emoji": "🍥", "description": "Crunchyroll premium"},
"100082": {"emoji": "🧾", "description": "Josh_Premium_100082"},
"authgop": {"emoji": "🛡️", "description": "Josh_Premium_Authgop"},
"mtacc": {"emoji": "📋", "description": "Josh_Premium_MTACC"},
"garena": {"emoji": "⚡", "description": "Josh_Premium_Garena"},
"roblox": {"emoji": "🧊", "description": "Josh_Premium_Roblox"},
"paypal": {"emoji": "💸", "description": "Josh_Premium_PayPal"},
"instagram": {"emoji": "📷", "description": "Josh_Premium_Instagram"},
"youtube": {"emoji": "📺", "description": "Josh_Premium_YouTube"},
"steam": {"emoji": "♨️", "description": "Josh_Premium_Steam"},
"epicgames": {"emoji": "🎯", "description": "Josh_Premium_Epic Games"},
"riotgames": {"emoji": "👊", "description": "Josh_Premium_Riot Games"},
"discord": {"emoji": "👾", "description": "Josh_Premium_Discord"},
"amazon": {"emoji": "📦", "description": "Josh_Premium_Amazon"},
"ebay": {"emoji": "🏷️", "description": "Josh_Premium_eBay"},
"spotify": {"emoji": "🎵", "description": "Josh_Premium_Spotify"},
"hulu": {"emoji": "📽️", "description": "Josh_Premium_Hulu"},
"disneyplus": {"emoji": "🧚", "description": "Josh_Premium_Disney+"},
"onlyfans": {"emoji": "🔞", "description": "Josh_Premium_OnlyFans"},
"linkedin": {"emoji": "💼", "description": "Josh_Premium_LinkedIn"},
"github": {"emoji": "🧑‍💻", "description": "Josh_Premium_GitHub"},
"apple": {"emoji": "🍏", "description": "Josh_Premium_Apple ID"},
"microsoft": {"emoji": "🪟", "description": "Josh_Premium_Microsoft"},
"yahoo": {"emoji": "📧", "description": "Josh_Premium_Yahoo"},
"gmail": {"emoji": "✉️", "description": "Josh_Premium_Gmail"},
"hotmail": {"emoji": "📨", "description": "Josh_Premium_Hotmail"},
"bank": {"emoji": "🏦", "description": "Josh_Premium_Bank"},
"crypto": {"emoji": "💱", "description": "Josh_Premium_Crypto"},
"binance": {"emoji": "🟡", "description": "Josh_Premium_Binance"},
"coinbase": {"emoji": "🪙", "description": "Josh_Premium_Coinbase"},
"twitch": {"emoji": "🎥", "description": "Josh_Premium_Twitch"},
"nintendo": {"emoji": "🍄", "description": "Josh_Premium_Nintendo"},
"playstation": {"emoji": "🌀", "description": "Josh_Premium_PlayStation"},
"xbox": {"emoji": "💚", "description": "Josh_Premium_Xbox"},
"uber": {"emoji": "🚗", "description": "Josh_Premium_Uber"},
"airbnb": {"emoji": "🏠", "description": "Josh_Premium_Airbnb"},
"telegram": {"emoji": "✈️", "description": "Josh_Premium_Telegram"},
"pubg": {"emoji": "🏹", "description": "Josh_Premium_PUBG"},
"tiktok": {"emoji": "🎶", "description": "Josh_Premium_TikTok"},
"vivamax": {"emoji": "🎬", "description": "Josh_Premium_Vivamax"},
"pornhub": {"emoji": "🍑", "description": "Josh_Premium_Pornhub"},
"freefire": {"emoji": "🔥", "description": "Josh_Premium_Free Fire"},
"crossfire": {"emoji": "🔫", "description": "Josh_Premium_CrossFire"},
"warzone": {"emoji": "🪖", "description": "Josh_Premium_Warzone"},
"codashop": {"emoji": "🎁", "description": "Josh_Premium_Codashop"},
"valorant": {"emoji": "💣", "description": "Josh_Premium_Valorant"},
        "hbo": {"emoji": "📺", "description": "HBO Max accounts"}
    },
    "KEY_DURATIONS": {
        "1h": 3600,
        "6h": 21600,
        "12h": 43200,
        "1d": 86400,
        "3d": 259200,
        "7d": 604800,
        "14d": 1209600,
        "30d": 2592000,
        "lifetime": None
    }
}

# === UTILITY FUNCTIONS ===
def create_directories():
    """Ensure all required directories exist"""
    if not os.path.exists(CONFIG["BACKUP_FOLDER"]):
        os.makedirs(CONFIG["BACKUP_FOLDER"])
    if not os.path.exists("database"):
        os.makedirs("database")

def get_today_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_timestamp():
    """Get current timestamp"""
    return datetime.now().timestamp()

def generate_random_key(length=12):
    """Generate a random alphanumeric key"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "PREMIUM-" + ''.join(random.choices(chars, k=length))

def hash_user_id(user_id):
    """Create a SHA256 hash of user ID for logging"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:8]

# === DATA MANAGEMENT ===
class DataManager:
    @staticmethod
    def load_keys():
        """Load keys data from file"""
        if os.path.exists(CONFIG["KEYS_FILE"]):
            try:
                with open(CONFIG["KEYS_FILE"], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Initialize missing sections
                    data.setdefault("keys", {})
                    data.setdefault("user_keys", {})
                    data.setdefault("logs", {})
                    data.setdefault("usage", {})
                    data.setdefault("request_times", {})
                    return data
            except Exception as e:
                print(f"Error loading keys: {e}")
                return {"keys": {}, "user_keys": {}, "logs": {}, "usage": {}, "request_times": {}}
        return {"keys": {}, "user_keys": {}, "logs": {}, "usage": {}, "request_times": {}}

    @staticmethod
    def save_keys(data):
        """Save keys data with backup"""
        try:
            # Create backup
            backup_file = os.path.join(
                CONFIG["BACKUP_FOLDER"],
                f"keys_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            # Save current data
            with open(CONFIG["KEYS_FILE"], "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving keys: {e}")
            return False

    @staticmethod
    def log_activity(user_id, action, details=""):
        """Log user activity"""
        user_hash = hash_user_id(user_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "logs" not in keys_data:
            keys_data["logs"] = {}
        
        if user_hash not in keys_data["logs"]:
            keys_data["logs"][user_hash] = []
        
        keys_data["logs"][user_hash].append({
            "timestamp": timestamp,
            "action": action,
            "details": details
        })
        
        # Keep only the last 100 logs per user
        if len(keys_data["logs"][user_hash]) > 100:
            keys_data["logs"][user_hash] = keys_data["logs"][user_hash][-100:]

# === RATE LIMITING ===
def check_rate_limit(user_id):
    """Check if user is exceeding rate limits"""
    user_id = str(user_id)
    now = get_current_timestamp()
    
    if "request_times" not in keys_data:
        keys_data["request_times"] = {}
    
    if user_id not in keys_data["request_times"]:
        keys_data["request_times"][user_id] = []
    
    # Remove old timestamps (older than 1 minute)
    keys_data["request_times"][user_id] = [
        t for t in keys_data["request_times"][user_id] 
        if now - t < 60
    ]
    
    # Check if user has exceeded the limit
    if len(keys_data["request_times"][user_id]) >= CONFIG["ANTI_ABUSE_LIMIT"]:
        return False
    
    # Add current timestamp
    keys_data["request_times"][user_id].append(now)
    DataManager.save_keys(keys_data)
    return True

# === USER MANAGEMENT ===
class UserManager:
    @staticmethod
    def check_user_access(user_id):
        """Check if user has valid access"""
        user_id = str(user_id)
        return user_id in keys_data["user_keys"] and (
            keys_data["user_keys"][user_id] is None or 
            keys_data["user_keys"][user_id] > get_current_timestamp()
        )

    @staticmethod
    def check_user_limits(user_id):
        """Check if user hasn't exceeded daily limits"""
        user_id = str(user_id)
        today = get_today_date()
        
        if "usage" not in keys_data:
            keys_data["usage"] = {}
        
        if today not in keys_data["usage"]:
            keys_data["usage"][today] = {}
        
        if user_id not in keys_data["usage"][today]:
            keys_data["usage"][today][user_id] = 0
        
        return keys_data["usage"][today][user_id] < CONFIG["MAX_DAILY_GENERATIONS"]

    @staticmethod
    def increment_user_usage(user_id):
        """Increment user's daily usage counter"""
        user_id = str(user_id)
        today = get_today_date()
        
        if "usage" not in keys_data:
            keys_data["usage"] = {}
        if today not in keys_data["usage"]:
            keys_data["usage"][today] = {}
        if user_id not in keys_data["usage"][today]:
            keys_data["usage"][today][user_id] = 0
        
        keys_data["usage"][today][user_id] += 1
        DataManager.save_keys(keys_data)
        DataManager.log_activity(user_id, "account_generation")

    @staticmethod
    def get_remaining_generations(user_id):
        """Get remaining generations for today"""
        user_id = str(user_id)
        today = get_today_date()
        
        if not UserManager.check_user_access(user_id):
            return 0
        
        if "usage" not in keys_data or today not in keys_data["usage"] or user_id not in keys_data["usage"][today]:
            return CONFIG["MAX_DAILY_GENERATIONS"]
        
        return CONFIG["MAX_DAILY_GENERATIONS"] - keys_data["usage"][today][user_id]

# === ACCOUNT GENERATION ===
class AccountGenerator:
    @staticmethod
    def get_used_accounts():
        """Load used accounts from file"""
        try:
            with open(CONFIG["USED_ACCOUNTS_FILE"], "r", encoding="utf-8", errors="ignore") as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            print(f"Error loading used accounts: {e}")
            return set()

    @staticmethod
    def mark_accounts_used(accounts):
        """Mark accounts as used"""
        try:
            with open(CONFIG["USED_ACCOUNTS_FILE"], "a", encoding="utf-8") as f:
                f.write("\n".join(accounts) + "\n")
            return True
        except Exception as e:
            print(f"Error saving used accounts: {e}")
            return False

    @staticmethod
    def find_matching_accounts(domain, used_accounts):
        """Find accounts matching the requested domain"""
        matched_lines = []
        
        for db_file in CONFIG["DATABASE_FILES"]:
            if len(matched_lines) >= CONFIG["LINES_TO_SEND"]:
                break
            
            try:
                with open(db_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and domain.lower() in line.lower() and line not in used_accounts:
                            matched_lines.append(line)
                            if len(matched_lines) >= CONFIG["LINES_TO_SEND"]:
                                break
            except Exception as e:
                print(f"Error reading {db_file}: {e}")
                continue
        
        return matched_lines

    @staticmethod
    def create_accounts_file(domain, accounts):
        """Create a file with the generated accounts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temp/{domain}_premium_{timestamp}.txt"
        
        try:
            os.makedirs("temp", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"⭐ {CONFIG['DOMAINS'][domain]['emoji']} Premium {domain.upper()} Accounts ⭐\n")
                f.write(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"🔑 Total Accounts: {len(accounts)}\n\n")
                f.write("\n".join(accounts))
            return filename
        except Exception as e:
            print(f"Error creating accounts file: {e}")
            return None

# === BOT COMMANDS ===
async def start(update: Update, context: CallbackContext):
    """Handler for /start command"""
    if not check_rate_limit(update.message.chat_id):
        return
    
    welcome_msg = (
        "🌟 **Premium Account Generator Bot**\n\n"
        "This bot provides premium accounts for various platforms.\n\n"
        "🔑 To get started, redeem your access key with /key <your_key>\n"
        "🛠 After redeeming, use /generate to get accounts\n\n"
        "📌 Note: Each user has a daily generation limit.\n"
        "🛡️ Your privacy is protected with secure hashing."
    )
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    DataManager.log_activity(update.message.chat_id, "start_command")

async def help_command(update: Update, context: CallbackContext):
    """Handler for /help command"""
    if not check_rate_limit(update.message.chat_id):
        return
    
    help_msg = (
        "🆘 **Help Menu**\n\n"
        "🔑 /key <key> - Redeem your access key\n"
        "🛠 /generate - Generate premium accounts\n"
        "ℹ /help - Show this help message\n"
        "📊 /mystats - Show your usage statistics\n\n"
        "👨‍💻 Admin Commands:\n"
        "🔧 /genkey <duration> [quantity] - Generate new keys\n"
        "📊 /logs - View system logs\n"
        "📈 /stats - Show system statistics\n"
        "📢 /broadcast <message> - Send message to all users\n"
        "🔄 /backup - Create manual backup"
    )
    
    await update.message.reply_text(help_msg, parse_mode="Markdown")
    DataManager.log_activity(update.message.chat_id, "help_command")

async def generate_menu(update: Update, context: CallbackContext):
    """Handler for /generate command - shows domain selection menu"""
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    chat_id = str(update.message.chat_id)
    
    if not UserManager.check_user_access(chat_id):
        return await update.message.reply_text(
            "🔑 You need a valid key to use this feature!\n\n"
            "Use /key <your_key> to redeem your access key."
        )
    
    if not UserManager.check_user_limits(chat_id):
        return await update.message.reply_text(
            "⚠️ You've reached your daily generation limit!\n"
            f"Max {CONFIG['MAX_DAILY_GENERATIONS']} generations per day.\n"
            "Try again tomorrow or contact admin."
        )
    
    # Create two columns of buttons
    keyboard = []
    domains = list(CONFIG["DOMAINS"].keys())
    
    for i in range(0, len(domains), 2):
        row = []
        if i < len(domains):
            domain = domains[i]
            emoji = CONFIG["DOMAINS"][domain]["emoji"]
            row.append(InlineKeyboardButton(
                f"{emoji} {domain.capitalize()}",
                callback_data=f"generate_{domain}"
            ))
        if i + 1 < len(domains):
            domain = domains[i + 1]
            emoji = CONFIG["DOMAINS"][domain]["emoji"]
            row.append(InlineKeyboardButton(
                f"{emoji} {domain.capitalize()}",
                callback_data=f"generate_{domain}"
            ))
        if row:
            keyboard.append(row)
    
    # Add cancel button
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
    
    remaining = UserManager.get_remaining_generations(chat_id)
    
    await update.message.reply_text(
        f"🛠 **Premium Account Generator**\n\n"
        f"🔑 Remaining today: {remaining}/{CONFIG['MAX_DAILY_GENERATIONS']}\n\n"
        "Select a platform to generate accounts:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    DataManager.log_activity(update.message.chat_id, "generate_menu")

async def generate_accounts(update: Update, context: CallbackContext):
    """Callback handler for account generation"""
    query = update.callback_query
    await query.answer()
    
    if not check_rate_limit(query.message.chat_id):
        return
    
    chat_id = str(query.message.chat_id)
    
    if query.data == "cancel":
        await query.message.delete()
        await query.message.reply_text("❌ Operation cancelled.")
        DataManager.log_activity(chat_id, "generation_cancelled")
        return
    
    if not UserManager.check_user_access(chat_id):
        await query.message.reply_text("🔑 You need a valid key to use this feature!")
        return
    
    if not UserManager.check_user_limits(chat_id):
        await query.message.reply_text("⚠️ You've reached your daily generation limit!")
        return
    
    selected_domain = query.data.replace("generate_", "")
    
    if selected_domain not in CONFIG["DOMAINS"]:
        await query.message.reply_text("❌ Invalid selection!")
        return
    
    processing_msg = await query.message.reply_text(
        f"⚡ Generating {CONFIG['DOMAINS'][selected_domain]['emoji']} "
        f"{selected_domain.upper()} accounts...\n"
        "Please wait while we process your request..."
    )
    
    # Load used accounts and find matches
    used_accounts = AccountGenerator.get_used_accounts()
    matched_lines = AccountGenerator.find_matching_accounts(selected_domain, used_accounts)
    
    if not matched_lines:
        await processing_msg.delete()
        await query.message.reply_text(
            f"❌ No available {selected_domain} accounts found!\n"
            "Try another platform or check back later."
        )
        DataManager.log_activity(chat_id, "generation_failed", f"No {selected_domain} accounts available")
        return
    
    # Mark accounts as used
    if not AccountGenerator.mark_accounts_used(matched_lines):
        await processing_msg.delete()
        await query.message.reply_text("❌ Error processing accounts. Please try again.")
        return
    
    # Create the output file
    filename = AccountGenerator.create_accounts_file(selected_domain, matched_lines)
    if not filename:
        await processing_msg.delete()
        await query.message.reply_text("❌ Error creating accounts file.")
        return
    
    # Update user usage
    UserManager.increment_user_usage(chat_id)
    remaining = UserManager.get_remaining_generations(chat_id)
    
    # Send the file
    await asyncio.sleep(1)  # Small delay for better UX
    
    try:
        await processing_msg.delete()
        with open(filename, "rb") as f:
            await query.message.reply_document(
                document=InputFile(f, filename=os.path.basename(filename)),
                caption=(
                    f"✅ Successfully generated {len(matched_lines)} "
                    f"{CONFIG['DOMAINS'][selected_domain]['emoji']} "
                    f"{selected_domain.upper()} accounts!\n\n"
                    f"🔑 Remaining today: {remaining}/{CONFIG['MAX_DAILY_GENERATIONS']}\n\n"
                    f"📝 {CONFIG['DOMAINS'][selected_domain]['description']}"
                ),
                parse_mode="Markdown"
            )
        DataManager.log_activity(chat_id, "generation_success", f"{selected_domain} {len(matched_lines)} accounts")
    except Exception as e:
        print(f"Error sending file: {e}")
        await query.message.reply_text("❌ Error sending accounts file.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def redeem_key(update: Update, context: CallbackContext):
    """Handler for /key command - redeem access key"""
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    chat_id = str(update.message.chat_id)
    
    if len(context.args) != 1:
        return await update.message.reply_text(
            "⚠️ Usage: /key <your_key>\n\n"
            "Contact the admin if you don't have a key."
        )
    
    entered_key = context.args[0].upper()
    
    if entered_key not in keys_data["keys"]:
        DataManager.log_activity(chat_id, "key_attempt", "invalid_key")
        return await update.message.reply_text(
            "❌ Invalid key!\n\n"
            "Make sure you entered the correct key or contact the admin."
        )
    
    expiry = keys_data["keys"][entered_key]
    if expiry is not None and get_current_timestamp() > expiry:
        del keys_data["keys"][entered_key]
        DataManager.save_keys(keys_data)
        DataManager.log_activity(chat_id, "key_attempt", "expired_key")
        return await update.message.reply_text("❌ This key has expired!")
    
    keys_data["user_keys"][chat_id] = expiry
    del keys_data["keys"][entered_key]
    DataManager.save_keys(keys_data)
    
    expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
    
    await update.message.reply_text(
        f"✅ Key redeemed successfully!\n\n"
        f"🔑 Access granted until: {expiry_text}\n\n"
        "Use /generate to start getting premium accounts!",
        parse_mode="Markdown"
    )
    DataManager.log_activity(chat_id, "key_redeemed", f"expiry:{expiry_text}")

async def my_stats(update: Update, context: CallbackContext):
    """Handler for /mystats command - show user's statistics"""
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    chat_id = str(update.message.chat_id)
    today = get_today_date()
    
    if not UserManager.check_user_access(chat_id):
        return await update.message.reply_text(
            "🔑 You need a valid key to use this feature!\n\n"
            "Use /key <your_key> to redeem your access key."
        )
    
    expiry = keys_data["user_keys"][chat_id]
    expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
    
    today_usage = keys_data.get("usage", {}).get(today, {}).get(chat_id, 0)
    remaining = CONFIG["MAX_DAILY_GENERATIONS"] - today_usage
    
    stats_msg = (
        f"📊 **Your Statistics**\n\n"
        f"🔑 Access expires: {expiry_text}\n"
        f"📅 Today's usage: {today_usage}/{CONFIG['MAX_DAILY_GENERATIONS']}\n"
        f"🔄 Remaining today: {remaining}\n\n"
        f"🆔 Your secure ID: `{hash_user_id(chat_id)}`"
    )
    
    await update.message.reply_text(stats_msg, parse_mode="Markdown")
    DataManager.log_activity(chat_id, "viewed_stats")

# === ADMIN COMMANDS ===
async def generate_keys(update: Update, context: CallbackContext):
    """Handler for /genkey command - generate new access keys"""
    if update.message.chat_id != CONFIG["ADMIN_ID"]:
        return await update.message.reply_text("⛔ Admin access required!")
    
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    if len(context.args) < 1 or context.args[0] not in CONFIG["KEY_DURATIONS"]:
        return await update.message.reply_text(
            "⚠️ Usage: /genkey <duration> [quantity]\n\n"
            "Available durations: " + ", ".join(CONFIG["KEY_DURATIONS"].keys()) + "\n"
            "Example: /genkey 7d 5 (generates 5 keys with 7-day validity)"
        )
    
    duration = context.args[0]
    quantity = 1 if len(context.args) < 2 else min(int(context.args[1]), 20)  # Max 20 keys at once
    
    generated_keys = []
    for _ in range(quantity):
        new_key = generate_random_key()
        expiry = None if duration == "lifetime" else (
            get_current_timestamp() + CONFIG["KEY_DURATIONS"][duration]
        )
        keys_data["keys"][new_key] = expiry
        generated_keys.append(new_key)
    
    DataManager.save_keys(keys_data)
    
    keys_list = "\n".join(f"🔑 `{key}`" for key in generated_keys)
    duration_text = "Lifetime" if duration == "lifetime" else f"{duration} (expires {datetime.fromtimestamp(get_current_timestamp() + CONFIG['KEY_DURATIONS'][duration]).strftime('%Y-%m-%d %H:%M:%S')})"
    
    await update.message.reply_text(
        f"✅ Successfully generated {quantity} {'key' if quantity == 1 else 'keys'}!\n\n"
        f"⏳ Duration: {duration_text}\n\n"
        f"{keys_list}\n\n"
        "Send these keys to your users.",
        parse_mode="Markdown"
    )
    DataManager.log_activity(update.message.chat_id, "generated_keys", f"{quantity} keys, {duration}")

async def view_logs(update: Update, context: CallbackContext):
    """Handler for /logs command - view system logs"""
    if update.message.chat_id != CONFIG["ADMIN_ID"]:
        return await update.message.reply_text("⛔ Admin access required!")
    
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    if not keys_data.get("user_keys"):
        return await update.message.reply_text("ℹ️ No users have redeemed keys yet.")
    
    # Create detailed log
    log_text = "📊 **System Logs**\n\n"
    log_text += f"🔑 Total active keys: {len(keys_data['keys'])}\n"
    log_text += f"👥 Total users: {len(keys_data['user_keys'])}\n\n"
    
    # Active users with hashed IDs
    log_text += "👤 **Active Users:**\n"
    for user, expiry in keys_data["user_keys"].items():
        expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
        log_text += f"▸ User Hash: `{hash_user_id(user)}` - Expires: `{expiry_text}`\n"
    
    # Daily usage statistics
    if keys_data.get("usage"):
        log_text += "\n📈 **Daily Usage Statistics:**\n"
        for date, users in sorted(keys_data["usage"].items(), reverse=True)[:7]:  # Last 7 days
            total_gens = sum(users.values())
            unique_users = len(users)
            log_text += f"▸ {date}: {total_gens} gens by {unique_users} users\n"
    
    # Recent activity logs
    if keys_data.get("logs"):
        log_text += "\n🔍 **Recent Activity:**\n"
        recent_activity = []
        for user_hash, logs in keys_data["logs"].items():
            for log in logs[-3:]:  # Last 3 actions per user
                recent_activity.append((log["timestamp"], user_hash, log["action"], log.get("details", "")))
        
        # Sort by timestamp (newest first)
        recent_activity.sort(reverse=True, key=lambda x: x[0])
        
        for timestamp, user_hash, action, details in recent_activity[:10]:  # Show 10 most recent
            log_text += f"▸ {timestamp} | {user_hash} | {action}"
            if details:
                log_text += f" | {details}"
            log_text += "\n"
    
    # Send as a file if too long
    if len(log_text) > 3000:
        filename = f"temp/system_logs_{datetime.now().strftime('%Y%m%d')}.txt"
        os.makedirs("temp", exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(log_text)
        
        with open(filename, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename=os.path.basename(filename)),
                caption="📊 System logs"
            )
        os.remove(filename)
    else:
        await update.message.reply_text(log_text, parse_mode="Markdown")
    
    DataManager.log_activity(update.message.chat_id, "viewed_logs")

async def system_stats(update: Update, context: CallbackContext):
    """Handler for /stats command - show system statistics"""
    if update.message.chat_id != CONFIG["ADMIN_ID"]:
        return await update.message.reply_text("⛔ Admin access required!")
    
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    # Count used accounts
    try:
        with open(CONFIG["USED_ACCOUNTS_FILE"], "r", encoding="utf-8") as f:
            used_count = sum(1 for line in f if line.strip())
    except:
        used_count = 0
    
    # Count total available accounts
    total_count = 0
    for db_file in CONFIG["DATABASE_FILES"]:
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                total_count += sum(1 for line in f if line.strip())
        except:
            continue
    
    available_count = total_count - used_count
    
    # Calculate daily usage
    today = get_today_date()
    today_usage = sum(keys_data.get("usage", {}).get(today, {}).values(), 0)
    
    stats_text = (
        "📊 **System Statistics**\n\n"
        f"🔑 Active keys: {len(keys_data['keys'])}\n"
        f"👥 Active users: {len(keys_data['user_keys'])}\n\n"
        f"📦 Total accounts: {total_count}\n"
        f"✅ Available accounts: {available_count}\n"
        f"❌ Used accounts: {used_count}\n\n"
        f"📅 Today's generations: {today_usage}\n"
        f"👤 Unique users today: {len(keys_data.get('usage', {}).get(today, {}))}\n\n"
        f"🛡️ Rate limit: {CONFIG['ANTI_ABUSE_LIMIT']} requests/minute"
    )
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")
    DataManager.log_activity(update.message.chat_id, "viewed_stats")

async def broadcast_message(update: Update, context: CallbackContext):
    """Handler for /broadcast command - send message to all users"""
    if update.message.chat_id != CONFIG["ADMIN_ID"]:
        return await update.message.reply_text("⛔ Admin access required!")
    
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /broadcast <message>")
    
    message = " ".join(context.args)
    users = keys_data["user_keys"].keys()
    
    if not users:
        return await update.message.reply_text("ℹ️ No active users to broadcast to.")
    
    await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 **Admin Broadcast**\n\n{message}",
                parse_mode="Markdown"
            )
            success += 1
        except:
            failed += 1
        await asyncio.sleep(0.1)  # Rate limiting
    
    await update.message.reply_text(
        f"✅ Broadcast completed!\n\n"
        f"✔ Success: {success}\n"
        f"✖ Failed: {failed}"
    )
    DataManager.log_activity(update.message.chat_id, "broadcast", f"success:{success} failed:{failed}")

async def manual_backup(update: Update, context: CallbackContext):
    """Handler for /backup command - create manual backup"""
    if update.message.chat_id != CONFIG["ADMIN_ID"]:
        return await update.message.reply_text("⛔ Admin access required!")
    
    if not check_rate_limit(update.message.chat_id):
        return await update.message.reply_text("⚠️ Too many requests! Please wait a minute.")
    
    backup_file = os.path.join(
        CONFIG["BACKUP_FOLDER"],
        f"manual_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    try:
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(keys_data, f, indent=4)
        
        with open(backup_file, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename=os.path.basename(backup_file)),
                caption="✅ Manual backup created"
            )
        DataManager.log_activity(update.message.chat_id, "manual_backup")
    except Exception as e:
        await update.message.reply_text(f"❌ Error creating backup: {e}")

# === AUTO-BACKUP TASK ===
async def auto_backup(context: CallbackContext):
    """Periodic automatic backup task"""
    backup_file = os.path.join(
        CONFIG["BACKUP_FOLDER"],
        f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    try:
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(keys_data, f, indent=4)
        print(f"Auto-backup created: {backup_file}")
    except Exception as e:
        print(f"Error during auto-backup: {e}")

# === ERROR HANDLER ===
async def error_handler(update: Update, context: CallbackContext):
    """Handle errors in the bot"""
    error = context.error
    print(f"Update {update} caused error: {error}")
    
    if update and update.message:
        user_id = update.message.chat_id
        DataManager.log_activity(user_id, "error", str(error))
        
        await update.message.reply_text(
            "❌ An error occurred while processing your request.\n"
            "The admin has been notified. Please try again later."
        )
        
        # Notify admin about the error
        if user_id != CONFIG["ADMIN_ID"]:
            try:
                await context.bot.send_message(
                    chat_id=CONFIG["ADMIN_ID"],
                    text=f"⚠️ Error occurred for user {hash_user_id(user_id)}:\n{error}"
                )
            except:
                pass

# === MAIN FUNCTION ===
def main():
    """Initialize and run the bot"""
    # Create required directories
    create_directories()
    
    # Load keys data
    global keys_data
    keys_data = DataManager.load_keys()
    
    # Initialize bot
    app = Application.builder().token(CONFIG["TOKEN"]).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("generate", generate_menu))
    app.add_handler(CommandHandler("key", redeem_key))
    app.add_handler(CommandHandler("mystats", my_stats))
    
    # Admin commands
    app.add_handler(CommandHandler("genkey", generate_keys))
    app.add_handler(CommandHandler("logs", view_logs))
    app.add_handler(CommandHandler("stats", system_stats))
    app.add_handler(CommandHandler("broadcast", broadcast_message))
    app.add_handler(CommandHandler("backup", manual_backup))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(generate_accounts, pattern="^generate_"))
    app.add_handler(CallbackQueryHandler(lambda u, c: u.message.delete(), pattern="^cancel$"))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Add periodic backup job
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(
            auto_backup,
            interval=CONFIG["AUTO_BACKUP_INTERVAL"],
            first=10
        )
    
    print("🤖 Premium Account Generator Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
