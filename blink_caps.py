#!/usr/bin/env python3
"""
Caps Lock LED Blinker
Blinks the Caps Lock LED light a specified number of times
Usage: python blink_caps.py <number_of_blinks>
"""

import sys
import time
import ctypes
from ctypes import wintypes
import subprocess

class CapsLockBlinker:
    def __init__(self):
        # Windows API constants
        self.VK_CAPITAL = 0x14  # Virtual key code for Caps Lock
        
        # Load Windows DLLs
        try:
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
        except Exception as e:
            print(f"❌ Error loading Windows DLL: {e}")
            self.user32 = None
            self.kernel32 = None
    
    def get_caps_lock_state(self):
        """Get current Caps Lock state"""
        if not self.user32:
            return False
        try:
            return bool(self.user32.GetKeyState(self.VK_CAPITAL) & 0x0001)
        except:
            return False
    
    def set_caps_lock_state(self, state):
        """Set Caps Lock state (True = ON, False = OFF)"""
        if not self.user32:
            return False
        
        try:
            current_state = self.get_caps_lock_state()
            if current_state != state:
                # Simulate Caps Lock key press
                self.user32.keybd_event(self.VK_CAPITAL, 0, 0, 0)  # Key down
                self.user32.keybd_event(self.VK_CAPITAL, 0, 2, 0)  # Key up
            return True
        except Exception as e:
            print(f"❌ Error setting Caps Lock state: {e}")
            return False
    
    def blink_caps_lock(self, times, duration=0.3):
        """Blink Caps Lock LED a specified number of times"""
        if not self.user32:
            print("❌ Windows API not available")
            return False
        
        print(f"💡 Blinking Caps Lock LED {times} time{'s' if times != 1 else ''}...")
        
        # Remember original state
        original_state = self.get_caps_lock_state()
        
        try:
            for i in range(times):
                # Turn ON
                self.set_caps_lock_state(True)
                print(f"💡 Blink {i+1}/{times} - ON")
                time.sleep(duration)
                
                # Turn OFF  
                self.set_caps_lock_state(False)
                print(f"💡 Blink {i+1}/{times} - OFF")
                
                # Wait between blinks (except for last one)
                if i < times - 1:
                    time.sleep(duration)
            
            # Restore original state
            self.set_caps_lock_state(original_state)
            print(f"✅ Caps Lock LED blinked {times} time{'s' if times != 1 else ''}")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ Blinking interrupted")
            # Restore original state
            self.set_caps_lock_state(original_state)
            return False
        except Exception as e:
            print(f"❌ Error during blinking: {e}")
            # Restore original state
            self.set_caps_lock_state(original_state)
            return False

def blink_answer_pattern(answer):
    """Blink LED based on quiz answer (A=1, B=2, C=3, D=4, E=5)"""
    blink_counts = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5
    }
    
    count = blink_counts.get(answer.upper(), 0)
    if count == 0:
        print(f"❌ Invalid answer '{answer}'. Use A, B, C, D, or E")
        return False
    
    print(f"📝 Answer {answer.upper()} = {count} blink{'s' if count != 1 else ''}")
    
    blinker = CapsLockBlinker()
    return blinker.blink_caps_lock(count)

def main():
    """Main function"""
    print("💡 Caps Lock LED Blinker")
    print("=" * 30)
    
    if len(sys.argv) < 2:
        print("Usage Options:")
        print("  python blink_caps.py <number>     # Blink N times")
        print("  python blink_caps.py <answer>     # Blink for quiz answer (A=1, B=2, etc.)")
        print("\nExamples:")
        print("  python blink_caps.py 3           # Blink 3 times")
        print("  python blink_caps.py B           # Blink 2 times (answer B)")
        return
    
    input_value = sys.argv[1].strip()
    
    # Check if it's a number
    if input_value.isdigit():
        times = int(input_value)
        if times <= 0 or times > 20:
            print("❌ Number of blinks must be between 1 and 20")
            return
        
        blinker = CapsLockBlinker()
        blinker.blink_caps_lock(times)
    
    # Check if it's a quiz answer (A, B, C, D, E)
    elif len(input_value) == 1 and input_value.upper() in 'ABCDE':
        blink_answer_pattern(input_value)
    
    else:
        print("❌ Invalid input. Use a number (1-20) or quiz answer (A, B, C, D, E)")

if __name__ == "__main__":
    main()
