#!/usr/bin/env python3

# Test script to debug the quiz system
import json
import ctypes
import time

def test_caps_lock_blinker():
    """Test the CapsLockBlinker functionality"""
    print("=== TESTING CAPS LOCK BLINKER ===")
    
    # Import the blinker class from screenshot.py
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from screenshot import CapsLockBlinker
    
    blinker = CapsLockBlinker()
    
    print("Testing single blink...")
    success = blinker.blink_caps_lock(1)
    print(f"Single blink result: {'✅ Success' if success else '❌ Failed'}")
    
    time.sleep(2)
    
    print("\nTesting double blink (like answer B)...")
    success = blinker.blink_caps_lock(2)
    print(f"Double blink result: {'✅ Success' if success else '❌ Failed'}")
    
def test_quiz_data_loading():
    """Test quiz data loading"""
    print("\n=== TESTING QUIZ DATA LOADING ===")
    
    try:
        with open('quiz_answers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            answers = data.get('answers', {})
            
        print(f"✅ Quiz data loaded successfully")
        print(f"📊 Questions available: {len(answers)}")
        
        for q_num, q_data in answers.items():
            answer = q_data['answer'].upper()
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            blinks = blink_counts.get(answer, 0)
            print(f"  Question {q_num}: Answer {answer} = {blinks} blinks")
            
        return answers
        
    except Exception as e:
        print(f"❌ Failed to load quiz data: {e}")
        return None

def simulate_question_processing(question_num, quiz_data):
    """Simulate processing a specific question"""
    print(f"\n=== SIMULATING QUESTION {question_num} PROCESSING ===")
    
    if str(question_num) not in quiz_data:
        print(f"❌ Question {question_num} not found in data")
        return False
        
    answer_data = quiz_data[str(question_num)]
    answer = answer_data['answer'].upper()
    
    blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    blink_count = blink_counts.get(answer, 0)
    
    if blink_count == 0:
        print(f"❌ Invalid answer '{answer}'")
        return False
    
    print(f"📝 Question {question_num}: Answer {answer}")
    print(f"💡 Expected blinks: {blink_count}")
    
    # Test the actual blinking
    from screenshot import CapsLockBlinker
    blinker = CapsLockBlinker()
    success = blinker.blink_caps_lock(blink_count)
    
    if success:
        print(f"🎉 Successfully blinked {blink_count} times for answer {answer}!")
        return True
    else:
        print("❌ Failed to blink")
        return False

if __name__ == "__main__":
    print("🔧 QUIZ SYSTEM DEBUG TEST")
    print("=" * 40)
    
    # Test 1: Caps Lock Blinker
    test_caps_lock_blinker()
    
    # Test 2: Quiz data loading
    quiz_data = test_quiz_data_loading()
    
    # Test 3: Question processing
    if quiz_data:
        available_questions = list(quiz_data.keys())
        if available_questions:
            test_question = available_questions[0]
            simulate_question_processing(test_question, quiz_data)
    
    print("\n🏁 Test completed!")
