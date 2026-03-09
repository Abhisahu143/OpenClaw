import os
import threading
import traceback
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent import start_chat_session, handle_message

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# In-memory storage for active chats (map of chat_id to Gemini ChatSession)
active_sessions = {}

# --- Telegram Bot Logic ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text("Hello! I am your OpenClaw-like Agentic AI. How can I assist you today?")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Passes user text to the Gemini Agent and replies with the result."""
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    # Send a typing action to Telegram while processing 
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Create a new session if one doesn't exist for this user
    if chat_id not in active_sessions:
        active_sessions[chat_id] = start_chat_session()
        
    chat_session = active_sessions[chat_id]
    
    try:
        # Pass the message to the Agentic Function Loop
        reply_text = handle_message(chat_session, user_text)
        await update.message.reply_text(reply_text)
    except Exception as e:
        print(f"Error handling message: {traceback.format_exc()}")
        await update.message.reply_text(f"Sorry, an error occurred while processing: {str(e)}")

def run_telegram_bot():
    """Starts the Telegram bot polling loop."""
    print("Starting Telegram Bot...")
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN environment variable not set!")
        return

    # Build the Application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Run the bot in polling mode (synchronous run call blocks thread)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


# --- Flask Web Server Logic ---
# Render requires a web service to bind to a port within a specific timeframe (usually 60 seconds).
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "OpenClaw AI Clone is running! The background Telegram bot is active."

def run_flask():
    """Starts the fake Flask server to satisfy Render's Port binding check."""
    # Render provides a PORT environment variable dynamically
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Web Server on port {port}...")
    # host='0.0.0.0' is required on Render to expose the API publicly
    flask_app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    # We will run the Telegram Bot polling loop in a clean background thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # The main thread runs the Flask server to bind the Render Port
    run_flask()
