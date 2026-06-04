#!/bin/sh
set -e

# Auto-copy example configs on first run (volume is empty)
[ -f /app/config/runtime.yml ] || \
    cp /app/config.examples/runtime.yml.example /app/config/runtime.yml

[ -f /app/config/chat_sys_prompt.txt ] || \
    cp /app/config.examples/chat_sys_prompt.txt.example /app/config/chat_sys_prompt.txt

# Wait for Web GUI setup to complete before starting the bot
if [ ! -f /app/data/config.yaml ]; then
    echo "⏳ Waiting for Web GUI setup to complete..."
    echo "   Open your browser and go to http://localhost:17860 to finish setup"
    until [ -f /app/data/config.yaml ]; do
        sleep 3
    done
    echo "✅ Setup complete, starting Bot..."
fi

exec uv run python main.py
