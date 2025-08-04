#!/usr/bin/env python3
"""
Telegram Music Bot - Main Entry Point
Provides seamless music downloads with Flask web server and webhook for Render deployment
"""

import logging
import os
import time
import asyncio
from flask import Flask, jsonify, render_template, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import (
    start_command, help_command, handle_spotify_url, 
    handle_button_callback, handle_message
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for Render deployment
app = Flask(__name__)
bot_status = {"running": False, "start_time": time.time()}

# Global bot application
application = None

@app.route('/')
def home():
    """Simple status page."""
    return "MusicFlow Bot is running!"

@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy", 
        "timestamp": time.time(),
        "bot_running": bot_status["running"],
        "service": "Telegram Music Bot"
    })

@app.route('/status')
def status_page():
    """Beautiful status page for the bot."""
    try:
        return render_template('status.html')
    except:
        return f"""
        <html>
        <head><title>MusicFlow Bot Status</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎵 MusicFlow Bot Status</h1>
            <p>Bot is ✅ Running</p>
            <p>Uptime: {int(time.time() - bot_status['start_time'])} seconds</p>
            <p>Service: Telegram Music Download Bot</p>
            <p>Ready for deployment on Render!</p>
        </body>
        </html>
        """

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram."""
    global application
    try:
        if application:
            # Get update from request
            update_dict = request.get_json()
            if update_dict:
                # Create Update object
                update = Update.de_json(update_dict, application.bot)
                
                # Process update in background
                asyncio.create_task(application.process_update(update))
                
        return '', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return '', 200

async def setup_bot():
    """Set up the Telegram bot application."""
    global application
    
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return None
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Initialize the application
    await application.initialize()
    await application.start()
    
    # Set webhook URL (Render will provide the URL)
    webhook_url = os.getenv("RENDER_EXTERNAL_URL", "")
    if webhook_url:
        webhook_url += "/webhook"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    else:
        logger.info("No webhook URL set - bot will work in polling mode if deployed locally")
    
    # Update bot status
    bot_status["running"] = True
    logger.info("Telegram bot configured successfully")
    
    return application

def main():
    """Run Flask web server with webhook support for Render deployment."""
    print("🎵 Starting MusicFlow Bot with Flask Web Server...")
    
    # Get port from environment (Render provides this dynamically)
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Port configuration: {port}")
    
    # Set up bot with webhook support
    print("🤖 Setting up Telegram bot with webhook...")
    try:
        # Run bot setup in asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(setup_bot())
        logger.info("Bot setup completed")
    except Exception as e:
        logger.error(f"Failed to setup bot: {e}")
        bot_status["running"] = False
    
    # Start Flask web server
    print("🚀 Starting Flask web server...")
    print("🌐 Bot will receive updates via webhook")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )

if __name__ == "__main__":
    main()