#!/bin/bash
# Start both Flask web server and Telegram bot for Render deployment

echo "🎵 Starting MusicFlow Bot Services..."

# Start Flask web server in background
echo "🌐 Starting Flask web server..."
python main.py &
WEB_PID=$!

# Wait a moment for web server to start
sleep 3

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
python bot_runner.py &
BOT_PID=$!

# Wait for both processes
wait $WEB_PID $BOT_PID