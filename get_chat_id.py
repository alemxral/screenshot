#!/usr/bin/env python3
"""
Get Chat ID for Telegram Bot
Run this after sending a message to your bot
"""

import requests
import json

BOT_TOKEN = "8370676217:AAEtdFxWz2oPRNjBrwmzGMJPVePqRloWaEw"

def get_chat_id():
    """Get your chat ID from bot updates"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        print("📱 Getting your chat ID...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['result']:
                # Get the most recent message
                latest_message = data['result'][-1]
                chat_id = latest_message['message']['chat']['id']
                
                print(f"✅ Your Chat ID: {chat_id}")
                
                # Update the config file
                config = {
                    "bot_token": BOT_TOKEN,
                    "chat_id": chat_id,
                    "created_at": "2025-09-14T20:00:00.000Z"
                }
                
                with open('telegram_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✅ Configuration saved to telegram_config.json")
                return chat_id
            else:
                print("❌ No messages found. Send a message to your bot first!")
                print("1. Go to Telegram")
                print("2. Search for your bot")
                print("3. Send any message (like 'hello')")
                print("4. Run this script again")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Telegram Chat ID Setup")
    print("=" * 30)
    
    get_chat_id()
