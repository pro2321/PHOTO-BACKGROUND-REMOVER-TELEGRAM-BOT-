import config
import db_helpers
import safety_check
import image_processing
import os
import time
from collections import deque
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# State for processing lock
PROCESSING = 0

# Helper to check admin status
def is_admin(user_id):
    return user_id in config.ADMIN_IDS

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Initialize user data if first time
    if 'initialized' not in context.user_data:
        context.user_data['initialized'] = True
        context.user_data['violations'] = 0
        context.user_data['banned'] = False
        context.user_data['daily_limit'] = 3
        context.user_data['last_used_date'] = None
        context.user_data['db_msg_id'] = None
        context.user_data['is_processing'] = False
        context.user_data['msg_timestamps'] = deque(maxlen=10)
    
    # Add user to global list (for /sendmsgall)
    db_helpers.add_user_to_db(context, user.id)
    
    # Send welcome message with terms of service
    welcome_text = (
        f"Welcome, {user.first_name}.\n\n"
        f"Your Name: {user.first_name}\n"
        f"Your User ID: <code>{user.id}</code>\n\n"
        "This bot removes the background from your photos. "
        "Just send me a photo to get started.\n\n"
        "For more details on how to use the bot, type /help.\n\n"
        "By using this bot, you accept our "
        '<a href="https://telegra.ph/TERMS-OF-SERVICE-REMOVE-BG-11-14">Terms of Service</a> and ' # এখানে আপনার লিংক দিন
        '<a href="https://telegra.ph/PRIVACY-POLICY-REMOVE-BG-11-14">Privacy Policy</a>.' # এখানে আপনার লিংক দিন
    )
    
    # Define buttons
    buttons = [
        [InlineKeyboardButton("SUPPORT CHAT", url="https://t.me/Pro_Support_24_7_Bot/")], # এখানে আপনার লিংক দিন
        [InlineKeyboardButton("Show Remaining Credits", callback_data="show_credits")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    
    # Create or update the DB channel message
    await db_helpers.update_db_channel_message(context, user)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "<b>How to use this bot:</b>\n\n"
        "1. <b>Send a Photo:</b> Simply send any photo to me.\n"
        "2. <b>Safety Check:</b> I will first scan the photo for any explicit content. "
        "Uploading such content will result in a violation.\n"
        "3. <b>Background Removal:</b> If the photo is safe, I will remove its background and send it back to you.\n"
        "4. <b>Convert:</b> After receiving the processed photo, you can choose to convert it into other formats like JPG, PDF, or ZIP.\n\n"
        "<b>Limits and Rules:</b>\n"
        f"• You can process <b>3 photos per day</b>.\n"
        f"• Admins have no limits.\n"
        f"• If you get <b>5 violations</b> for explicit content, you will be banned.\n"
        f"• Spamming the bot (e.g., 10 messages in a few seconds) will also result in a ban.\n"
        f"• To appeal a ban, contact our <b>Support Chat</b> (see /start)."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    admin = is_admin(user_id)
    
    # Ensure limits are fresh
    db_helpers.check_daily_limit(context.user_data, admin)
    
    # Get user data
    violations = context.user_data.get('violations', 0)
    banned = context.user_data.get('banned', False)
    credits = context.user_data.get('daily_limit', 3)
    
    # Build status message
    status_text = (
        f"<b>📊 Your Current Status</b>\n\n"
        f"<b>Name:</b> {user.first_name}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n"
        f"<b>Account Type:</b> {'Admin' if admin else 'Regular User'}\n\n"
        f"<b>Credits Remaining:</b> {'Unlimited' if admin else credits}\n"
        f"<b>Violations:</b> {violations}/5\n"
        f"<b>Status:</b> {'🚫 Banned' if banned else '✅ Active'}"
    )
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)


async def show_credits_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    admin = is_admin(user_id)
    
    # Ensure limits are fresh
    db_helpers.check_daily_limit(context.user_data, admin)
    
    credits = context.user_data.get('daily_limit', 3)
    
    if admin:
        message = "You are an admin. You have <b>unlimited</b> credits."
    else:
        message = f"You have <b>{credits}</b> credits remaining today."
        
    await query.message.reply_text(message, parse_mode=ParseMode.HTML)


async def handle_spam_and_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = context.user_data
    
    # 1. Check if banned
    if user_data.get('banned', False):
        return True # User is banned
        
    # 2. Check for spam (Requirement #8)
    if not is_admin(user_id):
        timestamps = user_data.get('msg_timestamps', deque(maxlen=10))
        timestamps.append(time.time())
        user_data['msg_timestamps'] = timestamps
        
        # 10 messages in 5 seconds
        if len(timestamps) == 10 and (timestamps[-1] - timestamps[0]) < 5:
            user_data['banned'] = True
            ban_reason = f"**User Banned for Spamming**\nUser ID: `{user_id}`"
            await db_helpers.log_event_to_db(context, ban_reason)
            await update_db_channel_message(context, update.effective_user)
            
            button = [[InlineKeyboardButton("Contact Support", url="https://t.me/Pro_Support_24_7_Bot/")]] # এখানে আপনার লিংক দিন
            await update.message.reply_text(
                "You have been **banned** for spamming. "
                "Contact support if you believe this is a mistake.",
                reply_markup=InlineKeyboardMarkup(button)
            )
            return True # User just got banned

    return False # User is not banned


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = context.user_data

    # Check for spam or existing ban
    if await handle_spam_and_ban(update, context):
        return

    # Check concurrency lock (Requirement #5)
    if user_data.get('is_processing', False):
        await update.message.reply_text("I am currently processing your previous request. Please wait.")
        return

    user_data['is_processing'] = True
    
    try:
        # Download photo
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"{user.id}_input.jpg"
        await photo_file.download_to_drive(file_path)

        # 1. Sight Engine Check (Requirement #1)
        is_explicit = await safety_check.check_image(file_path)
        
        if is_explicit and not is_admin(user.id):
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                print(f"Could not delete message: {e}")
                
            user_data['violations'] = user_data.get('violations', 0) + 1
            await update.message.reply_text(
                "**Warning:** Your image was detected as explicit content. "
                "This violation has been recorded. "
                f"You now have {user_data['violations']} of 5 violations."
            )
            
            # Check for ban (Requirement #7)
            if user_data['violations'] >= 5:
                user_data['banned'] = True
                ban_reason = f"**User Banned for Violations**\nUser ID: `{user.id}`\nViolations: 5"
                await db_helpers.log_event_to_db(context, ban_reason)
                
                button = [[InlineKeyboardButton("Contact Support", url="LINK_HERE")]] # এখানে আপনার লিংক দিন
                await update.message.reply_text(
                    "You have been **banned** for accumulating 5 violations. "
                    "Contact support to appeal.",
                    reply_markup=InlineKeyboardMarkup(button)
                )
            
            await db_helpers.update_db_channel_message(context, user)
            return # Stop processing

        # 2. Check Daily Limit (Requirement #6)
        admin = is_admin(user.id)
        if not db_helpers.check_daily_limit(user_data, admin):
            await update.message.reply_text("You have reached your daily limit of 3 photo removals.")
            return

        # 3. Process Image
        processing_msg = await update.message.reply_text("Processing your image. Please wait...")
        processed_bytes = await image_processing.remove_background(file_path)
        
        if processed_bytes:
            # Use credit
            db_helpers.use_credit(user_data, admin)
            # Update DB channel
            await db_helpers.update_db_channel_message(context, user)
            
            # Save bytes for conversion
            context.user_data['last_processed_bytes'] = processed_bytes
            
            # Send processed image as document
            await update.message.reply_document(
                document=processed_bytes,
                filename="background_removed.png"
            )
            
            # Ask for conversion (Requirement: infinite formats)
            # We provide a few common ones as requested.
            buttons = [
                [InlineKeyboardButton("JPG", callback_data="convert_JPG"),
                 InlineKeyboardButton("PDF", callback_data="convert_PDF")],
                [InlineKeyboardButton("ZIP (PNG inside)", callback_data="convert_ZIP")]
                # আপনি এখানে বাটন যোগ করতে পারেন
            ]
            await update.message.reply_text(
                "Would you like to convert this file to another format?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await processing_msg.delete()

        else:
            await processing_msg.edit_text("Sorry, an error occurred while removing the background.")

    except Exception as e:
        print(f"Error in handle_photo: {e}")
        await update.message.reply_text("An error occurred. Please try again.")
        
    finally:
        # Clean up local file
        if os.path.exists(file_path):
            os.remove(file_path)
        # Release lock
        user_data['is_processing'] = False


async def handle_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    target_format = query.data.split('_')[1] # e.g., 'JPG'
    
    image_bytes = context.user_data.get('last_processed_bytes')
    
    if not image_bytes:
        await query.edit_message_text("Sorry, I cannot find the original image to convert. Please send a new photo.")
        return

    await query.edit_message_text(f"Converting to {target_format}...")
    
    converted_bytes, filename = await image_processing.convert_format(image_bytes, target_format)
    
    if converted_bytes:
        await query.message.reply_document(
            document=converted_bytes,
            filename=filename
        )
        await query.edit_message_text("Here is your converted file.")
    else:
        await query.edit_message_text(f"Sorry, I cannot convert to {target_format}.")

# Handler to ignore messages in groups/channels
async def ignore_non_private_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Requirement #12: Bot should not work in groups/channels
    print(f"Ignoring message from chat: {update.effective_chat.id}")
    return
    
