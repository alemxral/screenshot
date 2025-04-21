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

# --------------------- Iriun Webcam Process Management ---------------------
def kill_iriun_webcam():
    """
    Searches for processes with 'iriun' in their name and force-kills them.
    """
    try:
        # Run the tasklist command and capture output.
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        process_found = False
        for line in result.stdout.splitlines():
            if "iriun" in line.lower():
                process_name = line.split()[0]
                print(f"Found process: {process_name}. Attempting to kill it...")
                kill_cmd = ["taskkill", "/F", "/IM", process_name]
                kill_result = subprocess.run(kill_cmd, capture_output=True, text=True)
                print(kill_result.stdout.strip())
                process_found = True
        if not process_found:
            print("No Iriun Webcam process found to kill.")
    except Exception as e:
        print("Error while trying to kill Iriun Webcam processes:", e)

def start_iriun_webcam():
    """
    Starts the Iriun Webcam process using the given executable path.
    """
    executable_path = r"C:\Program Files (x86)\Iriun Webcam\IriunWebcam.exe"
    if not os.path.exists(executable_path):
        print(f"Executable not found: {executable_path}")
        return
    try:
        subprocess.Popen(executable_path, shell=True)
        print("Iriun Webcam has been restarted.")
    except Exception as e:
        print("Error starting Iriun Webcam:", e)

# --------------------- Main Loop Integration ---------------------
async def main_loop():
    print("Hotkeys:")
    print("  Shift+Alt: Take a screenshot and push to git")
    print("  Right Arrow: Mute microphone")
    print("  Left Arrow: Unmute microphone")
    print("  F2: Kill (close) Iriun Webcam process")
    print("  F3: Restart Iriun Webcam")
    print("  Esc: Exit the program")
    
    while True:
        # Screenshot trigger: Shift + Alt (both pressed simultaneously)
        if keyboard.is_pressed("tab"):
            # Create an asynchronous screenshot task.
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)  # Delay to avoid multiple triggers

        # Mute trigger: Right Arrow
        elif keyboard.is_pressed("right"):
            mute_microphone()
            await asyncio.sleep(0.5)
        # Unmute trigger: Left Arrow
        elif keyboard.is_pressed("left"):
            unmute_microphone()
            await asyncio.sleep(0.5)
        # Iriun Webcam kill trigger: F2
        elif keyboard.is_pressed("F2"):
            kill_iriun_webcam()
            await asyncio.sleep(0.5)
        # Iriun Webcam restart trigger: F3
        elif keyboard.is_pressed("F3"):
            start_iriun_webcam()
            await asyncio.sleep(0.5)
        # Exit trigger: Esc

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
    