#!/usr/bin/env python3
"""
Telegram Music Bot - Main Entry Point
Provides seamless music downloads with Flask web server for Render deployment
"""

import logging
import os
import time
from flask import Flask, jsonify, render_template

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for Render deployment
app = Flask(__name__)
bot_status = {"running": False, "start_time": time.time()}

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

def main():
    """Run Flask web server for Render deployment."""
    print("🎵 Starting MusicFlow Bot Web Server...")
    
    # Bot status is managed by start.sh script
    bot_status["running"] = True
    
    # Get port from environment (Render provides this dynamically)
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Port configuration: {port}")
    
    print("🚀 Starting Flask web server...")
    print("🤖 Bot runs separately via start.sh script")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )

if __name__ == "__main__":
    main()
