import asyncio
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

# Path to the JSON registry file
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

def update_registry(filename, timestamp):
    # Append the new entry to the registry list
    registry.append({"filename": filename, "upload_time": timestamp})
    # Write back the updated registry to the JSON file
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=4)

async def git_upload_async(filepath, filename):
    try:
        # Run git add for both the screenshot and the registry file
        proc = await asyncio.create_subprocess_exec(
            "git", "add", filepath, registry_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        commit_message = f"Add screenshot {filename} and update registry"
        proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", commit_message,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        proc = await asyncio.create_subprocess_exec(
            "git", "push",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        print(f"✅ Git: {commit_message} and pushed.")
    except Exception as e:
        print("Git error:", e)

async def process_screenshot(current_counter):
    filename = f"img{current_counter}.png"
    filepath = os.path.join(save_dir, filename)
    # Offload the screenshot capture to a thread (since it's blocking)
    await asyncio.to_thread(pyautogui.screenshot, filepath)
    print(f"✅ Screenshot saved to {filepath}")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    update_registry(filename, current_time)
    print(f"✅ Registry updated with {filename} at {current_time}")

    await git_upload_async(filepath, filename)

async def main_loop():
    global counter
    while True:
        if keyboard.is_pressed("down") or keyboard.is_pressed("<"):
            # Schedule the screenshot processing asynchronously
            asyncio.create_task(process_screenshot(counter))
            counter += 1
            await asyncio.sleep(1)  # Prevent multiple triggers
        elif keyboard.is_pressed("esc"):
            print("👋 Exiting...")
            break
        # Small sleep to yield control and check keys frequently
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
