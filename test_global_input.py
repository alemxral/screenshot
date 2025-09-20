#!/usr/bin/env python3
"""
Test Global Keyboard Quiz Input
Tests the global keyboard listening functionality for quiz numbers
"""

import keyboard
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our functions from screenshot.py
from screenshot import CapsLockBlinker

def test_global_input():
    """Test global keyboard input capture"""
    print("🧪 Testing Global Keyboard Input")
    print("=" * 40)
    
    print("🎯 This will test if we can capture keyboard input globally")
    print("📝 Type some numbers and letters, then press ESC to stop")
    print("⚠️ Make sure to click on another window to test global capture!")
    print()
    
    captured_keys = []
    
    def capture_key(event):
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'esc':
                print(f"\n✅ Captured {len(captured_keys)} keys: {' '.join(captured_keys)}")
                return False  # Stop capture
            else:
                captured_keys.append(event.name)
                print(f"Key captured: {event.name}", end=" | ", flush=True)
    
    print("🚀 Starting global capture in 3 seconds...")
    time.sleep(3)
    print("📡 Global keyboard capture active! Press ESC to stop.")
    
    keyboard.on_press(capture_key)
    
    # Wait for ESC
    keyboard.wait('esc')
    
    print("⏹️ Global capture stopped")
    return True

def test_caps_lock_manual():
    """Manual test of caps lock blinking"""
    print("\n🧪 Manual Caps Lock Blink Test")
    print("=" * 40)
    
    blinker = CapsLockBlinker()
    
    print("Available tests:")
    print("1. Test Answer A (1 blink)")
    print("2. Test Answer B (2 blinks)")  
    print("3. Test Answer C (3 blinks)")
    print("4. Test Answer D (4 blinks)")
    print("5. Test Answer E (5 blinks)")
    print("6. Skip blink test")
    
    choice = input("Choose test (1-6): ").strip()
    
    if choice in ['1', '2', '3', '4', '5']:
        blinks = int(choice)
        answers = ['A', 'B', 'C', 'D', 'E']
        answer = answers[blinks - 1]
        
        print(f"💡 Testing Answer {answer} = {blinks} blink(s)")
        success = blinker.blink_caps_lock(blinks, duration=0.5)
        
        if success:
            print(f"✅ Answer {answer} blink test successful!")
            return True
        else:
            print(f"❌ Answer {answer} blink test failed!")
            return False
    else:
        print("⏭️ Skipping blink test")
        return True

def main():
    """Main test function"""
    print("🎯 Global Quiz Input System Test")
    print("=" * 50)
    
    # Test 1: Global keyboard capture
    print("Test 1: Global Keyboard Capture")
    test1_result = test_global_input()
    
    # Test 2: Caps Lock blinking
    print("\nTest 2: Caps Lock Blinking")
    test2_result = test_caps_lock_manual()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results:")
    print(f"  Global Keyboard: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  Caps Lock Blink: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! The global quiz system is ready!")
        print("\n🇫🇷 Usage with French keyboard:")
        print("   1. Run: python screenshot.py")
        print("   2. Press any trigger key: ' & é \" $")
        print("   3. Switch to any application window")
        print("   4. Type question number (1-20)")
        print("   5. Press Enter or wait for auto-submit")
        print("   6. Watch Caps Lock LED blink!")
        print("\n💡 The system will work globally - you can be in any application!")
    else:
        print("\n❌ Some tests failed. Check the setup.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
