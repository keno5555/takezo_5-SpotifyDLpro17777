#!/usr/bin/env python3
"""
Telegram Bot Runner - Standalone bot for production deployment
This runs the bot with polling when deployed to cloud platforms like Render
"""

import logging
import os
import asyncio
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

async def main():
    """Run the Telegram bot with polling."""
    print("🎵 Starting Telegram Music Bot...")
    
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot configured successfully - starting polling...")
    
    # Run the bot with polling
    await application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        # Try to run normally (works on Render/clean environments)
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            # Fallback for environments with existing event loop (like Replit)
            print("🔄 Using existing event loop (Replit environment)")
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            # Keep the process alive
            import time
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Bot stopped")
        else:
            raise
