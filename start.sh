#!/bin/bash
echo "🎵 Starting MusicFlow Bot Services..."

# Start Flask web server
echo "🌐 Starting Flask web server..."
python main.py &
WEB_PID=$!

# Wait for web server to stabilize
sleep 3

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
python bot_runner.py &
BOT_PID=$!

# Keep both alive
wait $WEB_PID $BOT_PID
