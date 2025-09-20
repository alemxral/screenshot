#!/usr/bin/env python3
"""
Test Telegram Vibrations
Sends a test vibration to your phone
"""

import requests
import json
import time

def test_vibrations():
    """Test different vibration patterns"""
    
    # Load config
    try:
        with open('telegram_config.json', 'r') as f:
            config = json.load(f)
    except:
        print("❌ No configuration found. Run get_chat_id.py first!")
        return
    
    bot_token = config['bot_token']
    chat_id = config['chat_id']
    
    if not chat_id:
        print("❌ No chat ID found. Send a message to your bot first!")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    print("🧪 Testing vibration patterns...")
    
    # Test different vibration strengths
    test_patterns = [
        ("🚨 URGENT VIBRATION TEST 🚨", "Single strong vibration"),
        ("📳 VIBRATION 1/3", "Pattern test 1"),
        ("📳 VIBRATION 2/3", "Pattern test 2"), 
        ("📳 VIBRATION 3/3", "Pattern test 3"),
        ("✅ VIBRATION TEST COMPLETE", "Final vibration")
    ]
    
    for i, (title, desc) in enumerate(test_patterns):
        message = f"""
{title}

📱 <b>{desc}</b>
🔢 <b>Test {i+1}/{len(test_patterns)}</b>

<i>Your phone should vibrate now!</i>
        """.strip()
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_notification': False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Test {i+1} sent!")
            else:
                print(f"❌ Test {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if i < len(test_patterns) - 1:
            time.sleep(2)  # Wait 2 seconds between tests
    
    print("\n🎉 Vibration test complete!")
    print("📱 Check your phone - you should have received multiple vibrating messages")

if __name__ == "__main__":
    test_vibrations()
