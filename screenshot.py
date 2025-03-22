import pyautogui
import keyboard
import time
import os
import glob
import subprocess

# Get the root path of the project (directory where the script is located)
project_root = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(project_root, "screenshots")
os.makedirs(save_dir, exist_ok=True)

# Determine the starting counter based on existing files
existing_files = glob.glob(os.path.join(save_dir, "img*.png"))
counter = len(existing_files) + 1

print("Press Down Arrow or '<' to take a screenshot. Press Esc to exit.")

def git_upload(filepath, filename):
    try:
        # Add the file to staging area
        subprocess.run(["git", "add", filepath], check=True)
        # Commit the file with a message
        commit_message = f"Add screenshot {filename}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        # Push the changes to remote
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Git: {commit_message} and pushed.")
    except subprocess.CalledProcessError as e:
        print("Git error:", e)

while True:
    try:
        # Check if DOWN ARROW or '<' key is pressed
        if keyboard.is_pressed("down") or keyboard.is_pressed("<"):
            filename = f"img{counter}.png"
            filepath = os.path.join(save_dir, filename)
            pyautogui.screenshot(filepath)
            print(f"✅ Screenshot saved to {filepath}")
            git_upload(filepath, filename)  # Upload changes to Git
            counter += 1
            time.sleep(1)  # Prevent multiple triggers

        elif keyboard.is_pressed("esc"):
            print("👋 Exiting...")
            break

    except Exception as e:
        print("Error:", e)
        break
