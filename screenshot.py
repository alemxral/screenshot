import asyncio
import pyautogui
import keyboard
import time
import os
import glob
import subprocess
import json
import threading

# --------------------- Screenshot & Git Functionality ---------------------

# Define project directories and load (or initialize) the registry.
project_root = os.path.dirname(os.path.abspath(__file__))
screenshots_dir = os.path.join(project_root, "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)
registry_path = os.path.join(project_root, "registry.json")

if os.path.exists(registry_path):
    with open(registry_path, "r") as f:
        registry = json.load(f)
else:
    registry = []

# Determine starting counter based on existing screenshot files.
existing_files = glob.glob(os.path.join(screenshots_dir, "img*.png"))
counter = len(existing_files) + 1

def update_registry(filename, timestamp):
    registry.append({"filename": filename, "upload_time": timestamp})
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=4)

async def git_push(filepath, filename):
    try:
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

        print(f"✅ Screenshot {filename} pushed to git.")
    except Exception as e:
        print("Git push error:", e)

def async_git_push(filepath, filename):
    # Launch a daemon thread that runs an asyncio event loop to push to git.
    threading.Thread(target=lambda: asyncio.run(git_push(filepath, filename)), daemon=True).start()

async def save_screenshot_async():
    global counter, registry
    filename = f"img{counter}.png"
    filepath = os.path.join(screenshots_dir, filename)
    # Capture screenshot asynchronously.
    screenshot = await asyncio.to_thread(pyautogui.screenshot)
    await asyncio.to_thread(screenshot.save, filepath)
    print(f"Screenshot saved to {filepath}")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    update_registry(filename, timestamp)
    async_git_push(filepath, filename)
    counter += 1

# --------------------- Microphone Mute/Unmute Functionality ---------------------

def mute_microphone():
    try:
        subprocess.run(["nircmd.exe", "mutesysvolume", "1", "microphone"], check=True)
        print("Microphone muted.")
    except subprocess.CalledProcessError as e:
        print("Error muting microphone:", e)

def unmute_microphone():
    try:
        subprocess.run(["nircmd.exe", "mutesysvolume", "0", "microphone"], check=True)
        print("Microphone unmuted.")
    except subprocess.CalledProcessError as e:
        print("Error unmuting microphone:", e)

# --------------------- Main Loop Integration ---------------------

async def main_loop():
    print("Press Right Arrow to mute microphone, Left Arrow to unmute, Shift+Alt to take a screenshot, Esc to exit.")
    while True:
        # Screenshot trigger: Shift + Alt
        if keyboard.is_pressed("tab"):
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)  # Prevent multiple triggers
        # Mute trigger: Right Arrow pressed.
        elif keyboard.is_pressed("right"):
            mute_microphone()
            await asyncio.sleep(0.5)
        # Unmute trigger: Left Arrow pressed.
        elif keyboard.is_pressed("left"):
            unmute_microphone()
            await asyncio.sleep(0.5)
        # Exit trigger: Esc pressed.
        elif keyboard.is_pressed("esc"):
            print("Exiting...")
            unmute_microphone()  # Ensure microphone is unmuted before exit.
            break

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())