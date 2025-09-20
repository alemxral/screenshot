#!/usr/bin/env python3
"""
Quiz Visual Notifier
Combines Telegram notifications with local LED blinking
"""

import json
import os
from telegram_bot import TelegramVibrationBot, load_github_quiz_data
from blink_caps import CapsLockBlinker

class QuizVisualNotifier:
    def __init__(self, config_file='telegram_config.json'):
        self.blinker = CapsLockBlinker()
        self.telegram_bot = None
        
        # Load Telegram config if available
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                self.telegram_bot = TelegramVibrationBot(
                    config['bot_token'], 
                    config['chat_id']
                )
                print("✅ Telegram bot loaded")
            except Exception as e:
                print(f"⚠️ Could not load Telegram config: {e}")
                print("📱 Only LED blinking will be available")
    
    def notify_answer(self, question_number, answer, use_telegram=True, use_led=True):
        """Send both Telegram notification and LED blink"""
        success_telegram = True
        success_led = True
        
        # Send Telegram notification
        if use_telegram and self.telegram_bot:
            print(f"📱 Sending Telegram notification...")
            success_telegram = self.telegram_bot.send_quiz_notification(question_number, answer)
        
        # Blink LED
        if use_led:
            print(f"💡 Blinking Caps Lock LED...")
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            count = blink_counts.get(answer.upper(), 0)
            if count > 0:
                success_led = self.blinker.blink_caps_lock(count, duration=0.4)
        
        return success_telegram and success_led
    
    def quick_answer_blink(self, answer):
        """Quick LED blink for an answer without Telegram"""
        blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
        count = blink_counts.get(answer.upper(), 0)
        
        if count == 0:
            print(f"❌ Invalid answer '{answer}'. Use A, B, C, D, or E")
            return False
        
        print(f"💡 Answer {answer.upper()} = {count} LED blink{'s' if count != 1 else ''}")
        return self.blinker.blink_caps_lock(count, duration=0.3)

def main():
    """Interactive quiz notifier"""
    print("🎯 Quiz Visual Notifier")
    print("=" * 40)
    
    notifier = QuizVisualNotifier()
    
    while True:
        print("\n📋 Options:")
        print("1. Quick answer blink (LED only)")
        print("2. Full notification (Telegram + LED)")
        print("3. Load answer from GitHub quiz data") 
        print("4. Exit")
        
        choice = input("\n➤ Choose option (1-4): ").strip()
        
        if choice == "1":
            answer = input("📝 Enter answer (A, B, C, D, E): ").strip()
            notifier.quick_answer_blink(answer)
        
        elif choice == "2":
            question = input("📝 Enter question number: ").strip()
            answer = input("📝 Enter answer (A, B, C, D, E): ").strip()
            
            if answer.upper() in 'ABCDE' and question.isdigit():
                notifier.notify_answer(question, answer)
            else:
                print("❌ Invalid input format")
        
        elif choice == "3":
            question = input("📝 Enter question number (1-20): ").strip()
            
            if question.isdigit():
                quiz_data = load_github_quiz_data()
                if quiz_data and question in quiz_data:
                    answer = quiz_data[question]['answer']
                    print(f"✅ Found answer: {answer}")
                    notifier.notify_answer(question, answer)
                else:
                    print("❌ Question not found in quiz data")
            else:
                print("❌ Please enter a valid question number")
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
