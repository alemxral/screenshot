import os
import time
import json
import glob
import asyncio
import subprocess
import threading
from ctypes import POINTER, cast

import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard
import pyautogui

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
    registry.append({"filename": filename, "timestamp": timestamp})
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=4)

async def git_push(filepath, filename):
    try:
        # Add the screenshot file and the registry file.
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

        print(f"Screenshot {filename} pushed to git.")
    except Exception as e:
        print("Git push error:", e)

def async_git_push(filepath, filename):
    # Launch a daemon thread that runs an asyncio event loop to push to git.
    threading.Thread(target=lambda: asyncio.run(git_push(filepath, filename)), daemon=True).start()

def save_screenshot():
    global counter, registry
    filename = f"img{counter}.png"
    filepath = os.path.join(screenshots_dir, filename)
    # Capture and save screenshot.
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    print(f"Screenshot saved to {filepath}")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    update_registry(filename, timestamp)
    # Push changes asynchronously to git.
    async_git_push(filepath, filename)
    counter += 1

# --------------------- Microphone Mute/Unmute Functionality ---------------------

def set_microphone_mute(mute=True):
    # Initialize COM for the current thread.
    comtypes.CoInitialize()
    try:
        # Retrieve the default microphone (capture device).
        mic = AudioUtilities.GetMicrophone()  # Requires a version of pycaw with this helper.
        if mic is None:
            print("No microphone found!")
            return
        # Activate the IAudioEndpointVolume interface.
        interface = mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(int(mute), None)
        print("Microphone muted." if mute else "Microphone unmuted.")
    except Exception as e:
        print("Error setting microphone mute state:", e)
    finally:
        comtypes.CoUninitialize()

# --------------------- Key Event Handlers ---------------------

def on_right_arrow(event):
    set_microphone_mute(True)

def on_left_arrow(event):
    set_microphone_mute(False)

def on_tab(event):
    save_screenshot()

# --------------------- Main Loop ---------------------

if __name__ == "__main__":
    print("Press Right Arrow to mute microphone, Left Arrow to unmute, Tab to take a screenshot, Esc to exit.")
    # Bind key events using the keyboard module.
    keyboard.on_press_key("right", on_right_arrow)
    keyboard.on_press_key("left", on_left_arrow)
    keyboard.on_press_key("tab", on_tab)
    # Wait until Esc is pressed.
    keyboard.wait("esc")
