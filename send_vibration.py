#!/usr/bin/env python3
"""
Quick Vibration Sender
Usage: python send_vibration.py <question_number>
"""

import sys
import json
import requests
import base64
from datetime import datetime

def load_config():
    """Load Telegram configuration"""
    try:
        with open('telegram_config.json', 'r') as f:
            config = json.load(f)
            
        # If no chat_id, try to get it automatically
        if not config.get('chat_id'):
            print("📱 Getting your chat ID...")
            chat_id = get_chat_id_from_bot(config['bot_token'])
            if chat_id:
                config['chat_id'] = chat_id
                # Save updated config
                with open('telegram_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"✅ Chat ID saved: {chat_id}")
            else:
                print("❌ Could not get chat ID. Send a message to your bot first!")
                return None
                
        return config
    except FileNotFoundError:
        print("❌ Configuration not found!")
        return None
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def get_chat_id_from_bot(bot_token):
    """Get chat ID from bot updates"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                latest_message = data['result'][-1]
                return latest_message['message']['chat']['id']
        return None
    except:
        return None

def load_quiz_data():
    """Load quiz data from GitHub"""
    url = "https://api.github.com/repos/alemxral/screenshot/contents/quiz_answers.json"
    
    try:
        print("📡 Loading latest quiz data from GitHub...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            file_data = response.json()
            content = base64.b64decode(file_data['content']).decode('utf-8')
            quiz_data = json.loads(content)
            answers = quiz_data.get('answers', {})
            print(f"✅ Loaded {len(answers)} quiz answers from GitHub")
            return answers
        else:
            print(f"❌ Failed to load quiz data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error loading quiz data: {e}")
        return None

def send_vibration_notification(config, question_number, answer):
    """Send vibration notification to Telegram with multiple messages for stronger vibration"""
    bot_token = config['bot_token']
    chat_id = config['chat_id']
    
    # Vibration patterns (A=1, B=2, C=3, D=4, E=5)
    patterns = {
        'A': ('1️⃣', 1, '• (1 vibration)'),
        'B': ('2️⃣', 2, '•• (2 vibrations)'),  
        'C': ('3️⃣', 3, '••• (3 vibrations)'),
        'D': ('4️⃣', 4, '•••• (4 vibrations)'),
        'E': ('5️⃣', 5, '••••• (5 vibrations)')
    }
    
    emoji, count, pattern = patterns.get(answer.upper(), ('❓', 0, 'Unknown'))
    
    # Main message
    main_message = f"""
🚨 <b>QUIZ VIBRATION ALERT</b> 🚨

📝 <b>Question:</b> {question_number}
✅ <b>Answer:</b> {answer.upper()}
📳 <b>Vibration Pattern:</b> {pattern}

📱 <b>VIBRATING {count} TIME{'S' if count != 1 else ''} NOW!</b>

⏰ <i>{datetime.now().strftime('%H:%M:%S')}</i>
    """.strip()
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        print(f"📱 Sending vibration notification to Telegram...")
        
        # Send main message
        payload = {
            'chat_id': chat_id,
            'text': main_message,
            'parse_mode': 'HTML',
            'disable_notification': False  # Enable notification for vibration
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            error_data = response.json() if response.content else {}
            print(f"❌ Telegram API Error: {response.status_code}")
            print(f"Response: {error_data}")
            return False
        
        print("✅ Main message sent!")
        
        # Send additional vibration messages for multiple vibrations
        if count > 1:
            import time
            for i in range(count - 1):
                time.sleep(1)  # Wait 1 second between vibrations
                
                vibration_msg = f"""
📳 <b>VIBRATION {i + 2}/{count}</b>

{emoji} <b>Question {question_number} = {answer.upper()}</b>
                """.strip()
                
                vibration_payload = {
                    'chat_id': chat_id,
                    'text': vibration_msg,
                    'parse_mode': 'HTML',
                    'disable_notification': False
                }
                
                vib_response = requests.post(url, json=vibration_payload, timeout=10)
                if vib_response.status_code == 200:
                    print(f"✅ Vibration {i + 2}/{count} sent!")
                else:
                    print(f"❌ Failed to send vibration {i + 2}")
        
        print("🎉 All vibration messages sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python send_vibration.py <question_number>")
        print("Example: python send_vibration.py 5")
        return
    
    question_number = sys.argv[1]
    
    # Validate question number
    if not question_number.isdigit() or not (1 <= int(question_number) <= 20):
        print("❌ Question number must be between 1 and 20")
        return
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Load quiz data from GitHub
    print("📡 Loading quiz data from GitHub...")
    quiz_answers = load_quiz_data()
    
    if not quiz_answers:
        print("❌ Could not load quiz data")
        return
    
    # Check if answer exists
    if question_number not in quiz_answers:
        print(f"❌ No answer found for question {question_number}")
        return
    
    answer = quiz_answers[question_number]['answer']
    print(f"📝 Question {question_number}: Answer = {answer}")
    
    # Send notification
    print("📱 Sending vibration notification...")
    if send_vibration_notification(config, question_number, answer):
        print("✅ Vibration notification sent!")
    else:
        print("❌ Failed to send notification")

if __name__ == "__main__":
    main()
