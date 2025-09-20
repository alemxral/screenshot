#!/usr/bin/env python3
"""
Test GitHub Quiz Data Fetching
Tests the improved GitHub data loading with better error handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screenshot import load_quiz_data_from_github, CapsLockBlinker

def test_github_connection():
    """Test GitHub API connection and data retrieval"""
    print("🧪 Testing GitHub Quiz Data Connection")
    print("=" * 50)
    
    # Test the GitHub loading function
    quiz_data = load_quiz_data_from_github()
    
    if quiz_data:
        print("\n🎉 GitHub test successful!")
        
        # Show some example questions
        print("\n📚 Quiz Data Preview:")
        for question_num, answer_data in list(quiz_data.items())[:5]:  # Show first 5
            answer = answer_data.get('answer', 'Unknown')
            blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
            blinks = blink_counts.get(answer, 0)
            print(f"   Question {question_num}: Answer {answer} = {blinks} blink{'s' if blinks != 1 else ''}")
        
        if len(quiz_data) > 5:
            print(f"   ... and {len(quiz_data) - 5} more questions")
        
        return True
    else:
        print("\n❌ GitHub test failed!")
        print("💡 Possible solutions:")
        print("   • Check your internet connection")
        print("   • Verify the repository URL is correct")
        print("   • Make sure quiz_answers.json exists in your repo")
        print("   • Check if the repository is public")
        return False

def test_blink_simulation():
    """Test the blinking functionality without actually blinking"""
    print("\n🧪 Testing Blink System")
    print("=" * 30)
    
    blinker = CapsLockBlinker()
    
    if blinker.user32:
        print("✅ Windows API available for Caps Lock control")
        current_state = blinker.get_caps_lock_state()
        print(f"💡 Current Caps Lock state: {'ON' if current_state else 'OFF'}")
        
        # Ask user if they want to test actual blinking
        test_real = input("\n🔥 Test real Caps Lock blinking? (y/n): ").strip().lower()
        
        if test_real == 'y':
            print("🔥 Testing 2 blinks (Answer B)...")
            success = blinker.blink_caps_lock(2, duration=0.5)
            if success:
                print("✅ Blink test successful!")
                return True
            else:
                print("❌ Blink test failed!")
                return False
        else:
            print("⏭️ Skipping real blink test")
            return True
    else:
        print("❌ Windows API not available - wrong platform?")
        return False

def main():
    """Main test function"""
    print("🎯 GitHub Quiz System Integration Test")
    print("=" * 60)
    
    # Test 1: GitHub connection
    github_result = test_github_connection()
    
    # Test 2: Blink system
    blink_result = test_blink_simulation()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary:")
    print(f"   GitHub Data Loading: {'✅ PASS' if github_result else '❌ FAIL'}")
    print(f"   Caps Lock Blinking: {'✅ PASS' if blink_result else '❌ FAIL'}")
    
    if github_result and blink_result:
        print("\n🎉 All systems ready!")
        print("\n🚀 Ready to use in screenshot.py:")
        print("   1. Run: python screenshot.py")
        print("   2. Press trigger key: ' & é \" $ (French keyboard)")
        print("   3. System will fetch latest data from GitHub")
        print("   4. Type question number from anywhere")
        print("   5. Watch Caps Lock LED blink!")
        print("\n⏰ Note: You now have 30 seconds to enter the question number")
        print("📡 Note: System always fetches latest data from GitHub first")
    else:
        print("\n⚠️ Some systems need attention before use")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
