#!/usr/bin/env python3
"""
Telegram Quiz Vibration Bot
Sends quiz answer notifications with vibration patterns to your phone
"""

import requests
import json
import time
import os
from datetime import datetime

class TelegramVibrationBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, message, parse_mode='HTML', disable_notification=False):
        """Send a text message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification  # False = notification with sound/vibration
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Message sent successfully")
                return True
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_multiple_vibration_messages(self, question_number, answer):
        """Send multiple messages to create multiple vibrations"""
        emoji, vibration_count, pattern = self.get_vibration_pattern(answer)
        
        # Send main message first
        main_message = f"""
🎯 <b>QUIZ VIBRATION ALERT</b> 🎯

📝 <b>Question:</b> {question_number}
✅ <b>Answer:</b> {answer.upper()}
📳 <b>Vibration Pattern:</b> {pattern}

📱 <b>VIBRATING {vibration_count} TIME{'S' if vibration_count != 1 else ''}...</b>
        """.strip()
        
        success = self.send_message(main_message, disable_notification=False)
        
        # Send additional vibration messages based on answer
        if success and vibration_count > 1:
            import time
            for i in range(vibration_count - 1):
                time.sleep(0.5)  # Wait between messages
                vibration_msg = f"📳 VIBRATION {i + 2}/{vibration_count}"
                self.send_message(vibration_msg, disable_notification=False)
        
        return success
    
    def get_vibration_pattern(self, answer):
        """Get vibration pattern for each answer"""
        patterns = {
            'A': ('1️⃣', 1, '• (short)'),
            'B': ('2️⃣', 2, '•• (short-short)'),  
            'C': ('3️⃣', 3, '••• (short-short-short)'),
            'D': ('4️⃣', 4, '•••• (short-short-short-short)'),
            'E': ('5️⃣', 5, '••••• (short-short-short-short-short)')
        }
        return patterns.get(answer.upper(), ('❓', 0, 'Unknown'))
    
    def send_quiz_notification(self, question_number, answer):
        """Send quiz answer notification with vibration pattern"""
        emoji, vibration_count, pattern = self.get_vibration_pattern(answer)
        
        message = f"""
🎯 <b>QUIZ ALERT</b> 🎯

📝 <b>Question:</b> {question_number}
✅ <b>Answer:</b> {answer.upper()}
{emoji} <b>Vibration Pattern:</b> {pattern}

📱 <b>ACTION REQUIRED:</b>
Make your phone vibrate <b>{vibration_count} time{'s' if vibration_count != 1 else ''}</b>

⏰ <i>{datetime.now().strftime('%H:%M:%S')}</i>
        """.strip()
        
        return self.send_message(message)
    
    def send_vibration_command(self, answer):
        """Send direct vibration command"""
        emoji, vibration_count, pattern = self.get_vibration_pattern(answer)
        
        message = f"""
📳 <b>VIBRATE NOW</b> 📳

{emoji} <b>{answer.upper()}</b> = {vibration_count} vibration{'s' if vibration_count != 1 else ''}

{pattern}
        """.strip()
        
        return self.send_message(message)
    
    def get_chat_id(self):
        """Get your chat ID (run this after messaging the bot)"""
        url = f"{self.base_url}/getUpdates"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['result']:
                    latest_message = data['result'][-1]
                    chat_id = latest_message['message']['chat']['id']
                    print(f"✅ Your Chat ID: {chat_id}")
                    return chat_id
                else:
                    print("❌ No messages found. Send a message to your bot first!")
                    return None
        except Exception as e:
            print(f"❌ Error getting chat ID: {e}")
            return None

def load_github_quiz_data(owner='alemxral', repo='screenshot', token=None):
    """Load quiz data from GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/quiz_answers.json"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    if token:
        headers['Authorization'] = f'token {token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            file_data = response.json()
            # Decode base64 content
            import base64
            content = base64.b64decode(file_data['content']).decode('utf-8')
            quiz_data = json.loads(content)
            return quiz_data.get('answers', {})
        else:
            print(f"❌ Failed to load quiz data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error loading quiz data: {e}")
        return None

def main():
    """Main function for testing and setup"""
    print("🤖 Telegram Quiz Vibration Bot Setup")
    print("=" * 50)
    
    # Configuration
    BOT_TOKEN = input("📱 Enter your Bot Token (from @BotFather): ").strip()
    
    if not BOT_TOKEN:
        print("❌ Bot token is required!")
        return
    
    # Get chat ID
    bot = TelegramVibrationBot(BOT_TOKEN, None)
    print("\n📝 Now send any message to your bot in Telegram...")
    input("Press Enter after you've sent a message to your bot...")
    
    chat_id = bot.get_chat_id()
    if not chat_id:
        return
    
    # Update bot with chat ID
    bot.chat_id = chat_id
    
    # Save configuration
    config = {
        'bot_token': BOT_TOKEN,
        'chat_id': chat_id,
        'created_at': datetime.now().isoformat()
    }
    
    with open('telegram_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved to telegram_config.json")
    
    # Test notification
    test_question = input("\n🧪 Enter a question number to test (1-20): ").strip()
    if test_question.isdigit():
        # Load quiz data
        quiz_answers = load_github_quiz_data()
        if quiz_answers and test_question in quiz_answers:
            answer = quiz_answers[test_question]['answer']
            bot.send_quiz_notification(test_question, answer)
            print(f"📱 Test notification sent for Question {test_question}!")
        else:
            print("❌ Question not found in quiz data. Sending test with answer 'B'...")
            bot.send_quiz_notification(test_question, 'B')
    
    print("\n🎉 Setup complete! You can now use the bot.")

if __name__ == "__main__":
    main()
