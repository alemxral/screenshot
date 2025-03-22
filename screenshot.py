import pyautogui
import keyboard
import time
import os
import glob

# Get the root path of the project (directory where the script is located)
project_root = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(project_root, "screenshots")
os.makedirs(save_dir, exist_ok=True)

# Determine the starting counter based on existing files
existing_files = glob.glob(os.path.join(save_dir, "img*.png"))
counter = len(existing_files) + 1

print("Press Down Arrow or '<' to take a screenshot. Press Esc to exit.")

while True:
    try:
        # Check if DOWN ARROW or '<' key is pressed
        if keyboard.is_pressed("down") or keyboard.is_pressed("<"):
            filename = f"img{counter}.png"
            filepath = os.path.join(save_dir, filename)
            pyautogui.screenshot(filepath)
            print(f"✅ Screenshot saved to {filepath}")
            counter += 1
            time.sleep(1)  # Prevent multiple triggers

        elif keyboard.is_pressed("esc"):
            print("👋 Exiting...")
            break

    except Exception as e:
        print("Error:", e)
        break
