#!/usr/bin/env python3
"""
Test Quiz Blink Functionality
Tests the CapsLockBlinker class and GitHub data loading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screenshot import CapsLockBlinker, load_quiz_data_from_github

def test_caps_lock_blinker():
    """Test the CapsLockBlinker class"""
    print("🧪 Testing CapsLockBlinker...")
    
    blinker = CapsLockBlinker()
    
    if not blinker.user32:
        print("❌ Windows API not available - running on wrong platform?")
        return False
    
    print("✅ CapsLockBlinker initialized successfully")
    
    # Test current state
    current_state = blinker.get_caps_lock_state()
    print(f"💡 Current Caps Lock state: {'ON' if current_state else 'OFF'}")
    
    # Test blinking with 2 blinks (answer B)
    print("\n🔥 Testing 2 blinks (answer B)...")
    success = blinker.blink_caps_lock(2, duration=0.3)
    
    if success:
        print("✅ Blinking test successful!")
        return True
    else:
        print("❌ Blinking test failed!")
        return False

def test_quiz_data_loading():
    """Test loading quiz data from GitHub"""
    print("\n🧪 Testing GitHub quiz data loading...")
    
    quiz_data = load_quiz_data_from_github()
    
    if quiz_data:
        print(f"✅ Successfully loaded {len(quiz_data)} quiz answers")
        
        # Show first few questions as examples
        count = 0
        for question_num, data in quiz_data.items():
            if count < 3:  # Show first 3
                answer = data.get('answer', 'Unknown')
                print(f"  📝 Question {question_num}: Answer = {answer}")
                count += 1
        
        if len(quiz_data) > 3:
            print(f"  ... and {len(quiz_data) - 3} more questions")
        
        return True
    else:
        print("❌ Failed to load quiz data")
        return False

def test_answer_blink_pattern():
    """Test blinking patterns for different answers"""
    print("\n🧪 Testing answer blink patterns...")
    
    blinker = CapsLockBlinker()
    blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    
    test_answer = input("Enter an answer to test (A, B, C, D, or E), or press Enter to skip: ").strip().upper()
    
    if test_answer in blink_counts:
        blink_count = blink_counts[test_answer]
        print(f"💡 Testing answer {test_answer} = {blink_count} blink{'s' if blink_count != 1 else ''}")
        
        success = blinker.blink_caps_lock(blink_count, duration=0.4)
        if success:
            print(f"✅ Answer {test_answer} blinking test successful!")
            return True
        else:
            print(f"❌ Answer {test_answer} blinking test failed!")
            return False
    else:
        print("⏭️ Skipping blink pattern test")
        return True

def main():
    """Main test function"""
    print("🎯 Quiz Blink Functionality Test")
    print("=" * 50)
    
    # Test 1: CapsLockBlinker functionality
    test1_result = test_caps_lock_blinker()
    
    # Test 2: GitHub data loading
    test2_result = test_quiz_data_loading()
    
    # Test 3: Answer blink patterns
    test3_result = test_answer_blink_pattern()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    print(f"  CapsLockBlinker: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  GitHub Data Loading: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"  Answer Blink Patterns: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    overall_success = test1_result and test2_result and test3_result
    print(f"\n🎉 Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n💡 The quiz blink functionality is ready to use!")
        print("   Press '$' key in screenshot.py to trigger quiz blink mode")

if __name__ == "__main__":
    main()
