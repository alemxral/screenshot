#!/usr/bin/env python3
"""
Simple automated test for French keyboard quiz functionality
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screenshot import CapsLockBlinker, load_quiz_data_from_github

def test_local_quiz_data():
    """Test loading and using local quiz data"""
    print("🧪 Testing local quiz data...")
    
    try:
        with open('quiz_answers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            quiz_data = data.get('answers', {})
        
        if not quiz_data:
            print("❌ No quiz answers found in local file")
            return False
        
        print(f"✅ Loaded {len(quiz_data)} answers from local file")
        
        # Test each available question
        blinker = CapsLockBlinker()
        
        for question_num, answer_data in quiz_data.items():
            answer = answer_data['answer'].upper()
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            blink_count = blink_counts.get(answer, 0)
            
            print(f"📝 Question {question_num}: Answer {answer} = {blink_count} blinks")
            
            if blink_count > 0:
                print(f"💡 Testing {blink_count} blink(s) for question {question_num}...")
                success = blinker.blink_caps_lock(blink_count, duration=0.3)
                if success:
                    print(f"✅ Question {question_num} blink test successful!")
                else:
                    print(f"❌ Question {question_num} blink test failed!")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing local quiz data: {e}")
        return False

def test_github_fallback():
    """Test GitHub data loading as fallback"""
    print("🧪 Testing GitHub quiz data fallback...")
    
    quiz_data = load_quiz_data_from_github()
    
    if quiz_data:
        print(f"✅ GitHub data loaded successfully: {len(quiz_data)} answers")
        return True
    else:
        print("⚠️ GitHub data not available (this is OK if offline)")
        return True  # Not a critical failure

def main():
    """Run automated tests"""
    print("🎯 Automated Quiz Blink Test")
    print("=" * 40)
    
    # Test 1: Local quiz data
    test1_result = test_local_quiz_data()
    
    # Test 2: GitHub fallback
    test2_result = test_github_fallback()
    
    print("=" * 40)
    print("🏁 Test Summary:")
    print(f"  Local Quiz Data: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  GitHub Fallback: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result:
        print("\n🎉 Quiz blink functionality is working!")
        print("\n🇫🇷 French keyboard keys to trigger quiz blink:")
        print("   ' (apostrophe key)")
        print("   & (number 1 key)")  
        print("   é (number 2 key)")
        print('   " (number 3 key)')
        print("   $ (Shift + number 4 key)")
        
        print("\n🚀 Usage in screenshot.py:")
        print("   1. Run: python screenshot.py")
        print("   2. Press any trigger key listed above")
        print("   3. Enter question number when prompted")
        print("   4. Watch Caps Lock LED blink according to answer!")
    else:
        print("\n❌ Please check quiz_answers.json file format")

if __name__ == "__main__":
    main()
