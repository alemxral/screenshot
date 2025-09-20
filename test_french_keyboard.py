#!/usr/bin/env python3
"""
Test French Keyboard Quiz Blink
Tests the quiz blink functionality with French keyboard keys
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screenshot import CapsLockBlinker

def load_local_quiz_data():
    """Load quiz data from local JSON file"""
    try:
        with open('quiz_answers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('answers', {})
    except Exception as e:
        print(f"❌ Error loading local quiz data: {e}")
        return None

def test_quiz_blink_with_question(question_num):
    """Test blinking with a specific question number"""
    quiz_data = load_local_quiz_data()
    
    if not quiz_data:
        print("❌ Could not load quiz data")
        return False
    
    print(f"📊 Available questions: {', '.join(quiz_data.keys())}")
    
    if str(question_num) not in quiz_data:
        print(f"❌ No answer found for question {question_num}")
        return False
    
    answer = quiz_data[str(question_num)]['answer'].upper()
    print(f"📝 Question {question_num}: Answer = {answer}")
    
    # Determine blink count (A=1, B=2, C=3, D=4, E=5)
    blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    blink_count = blink_counts.get(answer, 0)
    
    if blink_count == 0:
        print(f"❌ Invalid answer '{answer}' in quiz data")
        return False
    
    print(f"💡 Answer {answer} = {blink_count} blink{'s' if blink_count != 1 else ''}")
    
    # Create blinker and blink
    blinker = CapsLockBlinker()
    success = blinker.blink_caps_lock(blink_count, duration=0.4)
    
    if success:
        print(f"🎉 Quiz answer notification complete for Question {question_num}!")
        return True
    else:
        print("❌ Failed to blink Caps Lock LED")
        return False

def main():
    """Main test function"""
    print("🇫🇷 French Keyboard Quiz Blink Test")
    print("=" * 50)
    
    print("📋 Available French keyboard triggers for quiz blink:")
    print("  ' (apostrophe) - Key 4")
    print("  & (ampersand) - Key 1") 
    print("  é (e with accent) - Key 2")
    print('  " (quote) - Key 3')
    print("  $ (dollar) - Shift+4")
    print()
    
    # Load and show available quiz data
    quiz_data = load_local_quiz_data()
    if quiz_data:
        print(f"📚 Quiz data loaded successfully!")
        print(f"   Available questions: {', '.join(sorted(quiz_data.keys()))}")
        print()
        
        # Show answers for available questions
        for q_num in sorted(quiz_data.keys()):
            answer = quiz_data[q_num]['answer']
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            blinks = blink_counts.get(answer, 0)
            print(f"   Question {q_num}: Answer {answer} = {blinks} blink{'s' if blinks != 1 else ''}")
        print()
    else:
        print("❌ Could not load quiz data")
        return
    
    # Interactive test
    while True:
        question = input("Enter question number to test (or 'q' to quit): ").strip()
        
        if question.lower() == 'q':
            break
        
        if question.isdigit():
            print()
            test_quiz_blink_with_question(int(question))
            print()
        else:
            print("❌ Please enter a valid question number")
    
    print("👋 Test completed!")
    print()
    print("🚀 To use in screenshot.py:")
    print("   1. Run: python screenshot.py")
    print("   2. Press any of these keys: ' & é \" $")
    print("   3. Enter the question number when prompted")
    print("   4. Watch your Caps Lock LED blink!")

if __name__ == "__main__":
    main()
