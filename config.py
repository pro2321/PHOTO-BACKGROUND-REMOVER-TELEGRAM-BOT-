import os
from dotenv import load_dotenv

# .env file loading 
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

# Sight Engine API
SE_API_USER = os.getenv("SE_API_USER")
SE_API_SECRET = os.getenv("SE_API_SECRET")

# Remove.bg API
RBG_API = os.getenv("RBG_API")

# Telegram IDs
try:
    # অ্যাডমিন আইডি একটি কমা-সেপারেটেড স্ট্রিং হতে পারে (e.g., "123,456")
    ADMIN_IDS = [int(admin_id.strip()) for admin_id in os.getenv("ADMIN_ID", "").split(',')]
    DB_C_ID = int(os.getenv("DB_C_ID"))
except (ValueError, TypeError):
    raise ValueError("ADMIN_ID and DB_C_ID must be set as valid integers.")

if not all([SE_API_USER, SE_API_SECRET, RBG_API]):
    raise ValueError("One or more API environment variables are missing.")
