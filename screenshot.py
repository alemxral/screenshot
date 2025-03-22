import pyautogui
import keyboard
import time
import os
import glob
import subprocess
import json

# Get the root path of the project (directory where the script is located)
project_root = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(project_root, "screenshots")
os.makedirs(save_dir, exist_ok=True)

# Path to the JSON register file
registry_path = os.path.join(project_root, "registry.json")

# Load existing registry or initialize an empty list
if os.path.exists(registry_path):
    with open(registry_path, "r") as f:
        registry = json.load(f)
else:
    registry = []

# Determine the starting counter based on existing files
existing_files = glob.glob(os.path.join(save_dir, "img*.png"))
counter = len(existing_files) + 1

print("Press Down Arrow or '<' to take a screenshot. Press Esc to exit.")

def git_upload(filepath, filename):
    try:
        # Add both the screenshot and the registry file
        subprocess.run(["git", "add", filepath, registry_path], check=True)

        # Commit the file with a message
        commit_message = f"Add screenshot {filename} and update registry"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push the changes to remote
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Git: {commit_message} and pushed.")
    except subprocess.CalledProcessError as e:
        print("Git error:", e)

def update_registry(filename, timestamp):
    # Append the new entry to the registry list
    registry.append({"filename": filename, "upload_time": timestamp})
    # Write back the updated registry to the JSON file
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=4)

while True:
    try:
        # Check if DOWN ARROW or '<' key is pressed
        if keyboard.is_pressed("down") or keyboard.is_pressed("<"):
            filename = f"img{counter}.png"
            filepath = os.path.join(save_dir, filename)
            pyautogui.screenshot(filepath)
            print(f"✅ Screenshot saved to {filepath}")

            # Record the current time and update the registry
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            update_registry(filename, current_time)
            print(f"✅ Registry updated with {filename} at {current_time}")

            # Upload screenshot and registry file
            git_upload(filepath, filename)

            counter += 1
            time.sleep(1)  # Prevent multiple triggers

        elif keyboard.is_pressed("esc"):
            print("👋 Exiting...")
            break

    except Exception as e:
        print("Error:", e)
        break
