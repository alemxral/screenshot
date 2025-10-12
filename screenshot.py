# --- IMPORTS ---
import asyncio
import pyautogui
import keyboard
import time
import os
import glob
import subprocess
import json
import threading
import sys
import random
CREATE_NO_WINDOW = 0x08000000  # For subprocess.run/exec to suppress console windows on Windows
import ctypes
from ctypes import wintypes
import requests

# For white noise generation
import threading
import numpy as np
import sounddevice as sd

# Global variable for storing original microphone levels
original_mic_levels = {}

# White noise playback control
white_noise_thread = None
white_noise_stop_event = threading.Event()

def play_white_noise():
    """
    Play white noise in a background thread until stopped.
    """
    samplerate = 44100
    duration = 1  # seconds per chunk
    while not white_noise_stop_event.is_set():
        noise = np.random.normal(0, 0.1, int(samplerate * duration)).astype(np.float32)
        sd.play(noise, samplerate=samplerate, blocking=True)
    sd.stop()

def start_white_noise():
    global white_noise_thread, white_noise_stop_event
    if white_noise_thread is not None and white_noise_thread.is_alive():
        return
    white_noise_stop_event.clear()
    white_noise_thread = threading.Thread(target=play_white_noise, daemon=True)
    white_noise_thread.start()
    print("[NOISE] White noise playback started.")

def stop_white_noise():
    global white_noise_thread, white_noise_stop_event
    white_noise_stop_event.set()
    if white_noise_thread is not None:
        white_noise_thread.join(timeout=2)
        white_noise_thread = None
    print("[NOISE] White noise playback stopped.")


def human_type(text, min_delay=0.08, max_delay=0.22):
    """
    Type the given text simulating human speed by introducing
    a small random delay between each character. Punctuation
    causes slightly longer pauses.
    """
    try:
        for ch in str(text):
            # Use write for characters; special keys could be expanded
            pyautogui.write(ch, interval=0)
            # Slightly longer pause after punctuation
            pause = random.uniform(min_delay, max_delay)
            if ch in '.!,?:;':
                pause += random.uniform(0.06, 0.20)
            time.sleep(pause)
    except Exception as e:
        print(f"❌ human_type failed: {e}")

# Global variable for storing original microphone levels
original_mic_levels = {}

# --- HOTKEY: Up Arrow to send unsent screenshots/messages.json to Telegram group ---
def on_up_arrow():
    print("[HOTKEY] Up arrow pressed: Sending unsent screenshots and messages.json to Telegram group...")
    send_screenshots_and_messages()

keyboard.add_hotkey('up', on_up_arrow)
# Telegram
import requests



# Support PyInstaller: get correct base path for data files, but always save screenshots to the original script directory
def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_script_dir():
    # Always return the directory where the script/exe was launched from
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

project_root = get_base_path()
script_dir = get_script_dir()
TELEGRAM_CONFIG_PATH = os.path.join(project_root, "telegram_config.json")
SENT_REGISTRY_PATH = os.path.join(project_root, "sent_registry.json")

def load_telegram_config():
    with open(TELEGRAM_CONFIG_PATH, "r") as f:
        return json.load(f)

def load_sent_registry():
    if os.path.exists(SENT_REGISTRY_PATH):
        with open(SENT_REGISTRY_PATH, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_registry(sent_set):
    with open(SENT_REGISTRY_PATH, "w") as f:
        json.dump(list(sent_set), f, indent=2)

SENT_MESSAGES_PATH = os.path.join(project_root, "sent_messages.json")

def load_sent_messages():
    if os.path.exists(SENT_MESSAGES_PATH):
        with open(SENT_MESSAGES_PATH, "r") as f:
            return json.load(f)
    return []

def save_sent_messages(messages_list):
    with open(SENT_MESSAGES_PATH, "w") as f:
        json.dump(messages_list, f, indent=2)

def send_file_to_telegram(bot_token, chat_id, file_path, caption=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        response = requests.post(url, data=data, files=files)
    if response.ok:
        result = response.json()
        message_id = result.get("result", {}).get("message_id")
        return message_id
    return None

def send_text_to_telegram(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, data=data)
    if response.ok:
        result = response.json()
        message_id = result.get("result", {}).get("message_id")
        return message_id
    return None

def send_screenshots_and_messages():
    config = load_telegram_config()
    bot_token = config["TELEGRAM_BOT_TOKEN"]
    chat_id = config["TELEGRAM_GROUP_CHAT_ID"]
    sent = load_sent_registry()
    sent_messages = load_sent_messages()
    # Send unsent screenshots
    screenshots = sorted(glob.glob(os.path.join(screenshots_dir, "img*.png")))
    sent_any = False
    for img in screenshots:
        if img not in sent:
            message_id = send_file_to_telegram(bot_token, chat_id, img, caption=os.path.basename(img))
            if message_id:
                sent.add(img)
                sent_messages.append({"file_path": img, "message_id": message_id, "type": "screenshot"})
                sent_any = True
                print(f"Sent {img} to Telegram group (message ID: {message_id}).")
            else:
                print(f"Failed to send {img} to Telegram.")
    # Send messages.json content as a text message if not sent
    import hashlib
    messages_path = os.path.join(project_root, "messages.json")
    try:
        with open(messages_path, "r", encoding="utf-8") as f:
            messages_data = json.load(f)
        # Format all messages as text
        if isinstance(messages_data, list):
            for entry in messages_data:
                # Create a unique hash for each message entry
                entry_str = json.dumps(entry, sort_keys=True)
                entry_hash = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
                # Only send if not already sent
                if entry_hash not in sent:
                    text = "\n".join(f"{k}: {v}" for k, v in entry.items())
                    message_id = send_text_to_telegram(bot_token, chat_id, text)
                    if message_id:
                        sent_any = True
                        sent.add(entry_hash)
                        sent_messages.append({"entry_hash": entry_hash, "message_id": message_id, "type": "messages"})
                        print(f"Sent message entry to Telegram group (message ID: {message_id}).")
                    else:
                        print("Failed to send message entry to Telegram.")
        else:
            print("messages.json is not a list.")
    except Exception as e:
        print(f"Failed to send messages.json content: {e}")
    if sent_any:
        save_sent_registry(sent)
        save_sent_messages(sent_messages)
    else:
        print("No new files to send.")

screenshots_dir = os.path.join(script_dir, "screenshots")
registry_path = os.path.join(project_root, "registry.json")


# --- HOTKEY: Down Arrow to send unsent screenshots/messages.json to Telegram group ---
def on_down_arrow():

    print("[HOTKEY] Down arrow pressed: Sending unsent screenshots and messages.json to Telegram group...")
    # Download latest quiz_answers.json from GitHub Pages (primary) or raw GitHub (fallback)
    import requests, hashlib
    primary_url = "https://alemxral.github.io/screenshot/quiz_answers.json"
    fallback_url = "https://raw.githubusercontent.com/alemxral/screenshot/main/quiz_answers.json"
    local_path = os.path.join(project_root, "quiz_answers.json")
    updated = False
    try:
        resp = requests.get(primary_url, timeout=10)
        if resp.ok:
            with open(local_path, "wb") as f:
                f.write(resp.content)
            print(f"✅ quiz_answers.json replaced from {primary_url}!")
            # Show file content for debug
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    print("--- quiz_answers.json content ---")
                    print(f.read())
                    print("--- end of file ---")
            except Exception as e:
                print(f"[DEBUG] Could not read quiz_answers.json: {e}")
            try:
                CapsLockBlinker().blink_caps_lock(2)
            except Exception:
                pass
            updated = True
        else:
            print(f"Failed to download quiz_answers.json from {primary_url}: {resp.status_code}")
    except Exception as e:
        print(f"Error downloading quiz_answers.json from {primary_url}: {e}")
    if not updated:
        try:
            resp = requests.get(fallback_url, timeout=10)
            if resp.ok:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                print(f"✅ quiz_answers.json replaced from {fallback_url}!")
                # Show file content for debug
                try:
                    with open(local_path, "r", encoding="utf-8") as f:
                        print("--- quiz_answers.json content ---")
                        print(f.read())
                        print("--- end of file ---")
                except Exception as e:
                    print(f"[DEBUG] Could not read quiz_answers.json: {e}")
                try:
                    CapsLockBlinker().blink_caps_lock(2)
                except Exception:
                    pass
                updated = True
            else:
                print(f"Failed to download quiz_answers.json from {fallback_url}: {resp.status_code}")
        except Exception as e:
            print(f"Error downloading quiz_answers.json from {fallback_url}: {e}")
    if not updated:
        print("❌ Could not update quiz_answers.json from any source.")
    send_screenshots_and_messages()



# --- HOTKEY: Supr (Delete) to delete bot's sent messages from the group ---
def on_supr():
    print("[HOTKEY] Supr pressed: Deleting bot's sent messages from Telegram group...")
    import asyncio
    asyncio.run(delete_bot_messages())

keyboard.add_hotkey('delete', on_supr)

# --- HOTKEY: F10 to clear screenshots, messages.json, and register ---
def on_f10():
    print("[HOTKEY] F10 pressed: Clearing screenshots, messages.json, and register...")
    # Remove all screenshots
    for img in glob.glob(os.path.join(screenshots_dir, "img*.png")):
        try:
            os.remove(img)
            print(f"Deleted {img}")
        except Exception as e:
            print(f"Failed to delete {img}: {e}")

    # Clear all JSON files except quiz_answers.json and telegram_config.json
    for filename in os.listdir(project_root):
        if filename.endswith('.json') and filename not in ("quiz_answers.json", "telegram_config.json"):
            file_path = os.path.join(project_root, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
            print(f"Cleared {filename}")

keyboard.add_hotkey('f10', on_f10)



# --- Prevent multiple instances using Windows mutex (pywin32) ---
try:
    import win32event
    import win32api
    import winerror
    import sys
    mutex = win32event.CreateMutex(None, False, 'screenshot_app_unique_mutex')
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        print("Another instance of this program is already running. Exiting.")
        sys.exit(0)
except ImportError:
    print("pywin32 is not installed. Multiple instance prevention is disabled.")
# --- End mutex section ---

def install_required_packages():
    """
    Auto-installs required packages from requirements.txt if not available.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(script_dir, "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print("requirements.txt file not found. Creating it...")
        with open(requirements_file, 'w') as f:
            f.write("pyautogui==0.9.54\nkeyboard==0.13.5\npycaw==20230407\ncomtypes==1.2.0\n")    # Check if packages are installed by trying to import them
    missing_packages = []
    try:
        import pyautogui
        print("Package 'pyautogui' is already installed.")
    except ImportError:
        missing_packages.append('pyautogui')
    
    try:
        import keyboard
        print("Package 'keyboard' is already installed.")
    except ImportError:
        missing_packages.append('keyboard')
    
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        print("Package 'pycaw' and 'comtypes' are already installed.")
    except ImportError:
        missing_packages.append('pycaw')
        missing_packages.append('comtypes')
    
    # Install missing packages using requirements.txt
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], check=True, creationflags=CREATE_NO_WINDOW)
            print("All required packages installed successfully from requirements.txt.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages from requirements.txt: {e}")
            sys.exit(1)
    else:
        print("All required packages are already installed.")

# --------------------- Screenshot Functionality ---------------------
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
    counter += 1

def silent_unmute_microphone():
    """
    Restores normal microphone INPUT capture levels while keeping device available.
    """
    global mic_silenced_by_script, original_mic_levels
    success = False
    
    # Method 1: Restore original INPUT capture levels
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetAllDevices()
        restored_count = 0
        
        for device in devices:
            try:
                # Only target CAPTURE/INPUT devices (microphones)
                if (hasattr(device, 'dataflow') and device.dataflow == 1) or \
                   (device.FriendlyName and 
                    ("microphone" in device.FriendlyName.lower() or 
                     "mic" in device.FriendlyName.lower() or
                     "capture" in device.FriendlyName.lower()) and
                    device.state == 1):
                    
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    
                    # Restore original INPUT capture level if stored
                    if device.FriendlyName in original_mic_levels:
                        restored_input_level = original_mic_levels[device.FriendlyName]
                    else:
                        restored_input_level = 0.7  # Default to 70% capture sensitivity
                    
                    volume.SetMasterScalarVolume(restored_input_level, None)
                    volume.SetMute(0, None)  # Ensure not muted
                    
                    restored_count += 1
                    print(f"🔊 INPUT Restored: {device.FriendlyName} (Capture: {restored_input_level:.0%})")
                    
            except Exception as e:
                continue
        
        if restored_count > 0:
            success = True
            print(f"✅ {restored_count} microphone INPUT(s) restored to normal sensitivity!")
    except Exception as e:
        print(f"Input level restoration failed: {e}")
    
    # Method 2: Restore via nircmd RECORDING controls
    if mic_silenced_by_script:
        try:
            # Restore microphone recording volume to normal (70% = 45875 out of 65535)
            subprocess.run(["nircmd.exe", "setsysvolume", "45875", "default_record"], check=False)
            print("🔊 Microphone recording volume restored to 70% via nircmd")
            
            # Unmute the recording device
            subprocess.run(["nircmd.exe", "mutesysvolume", "0", "default_record"], check=False)
            print("🔊 Microphone recording unmuted via nircmd")
            
            success = True
        except Exception as e:
            print(f"nircmd recording restoration failed: {e}")
    
    # Method 3: Restore PowerShell microphone INPUT settings
    if mic_silenced_by_script:
        try:
            ps_command = '''
            # Restore microphone INPUT sensitivity to normal levels
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class AudioControl {
                    [DllImport("winmm.dll", SetLastError = true)]
                    public static extern uint waveInSetVolume(IntPtr hwo, uint dwVolume);
                }
"@

            # Restore microphone input volume to 70% (0xB333B333 in hex)
            $result = [AudioControl]::waveInSetVolume([IntPtr]::Zero, 0xB333B333)
            Write-Host "Microphone input sensitivity restored to normal"
            '''
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command], 
                         capture_output=True, text=True, check=False)
            print("🔊 Microphone INPUT sensitivity restored via PowerShell")
            success = True
        except Exception as e:
            print(f"PowerShell input restoration failed: {e}")
    
    if success:
        mic_silenced_by_script = False
        original_mic_levels.clear()
        print("🔊 NORMAL MODE: Microphone fully functional and capturing audio!")
    else:
        print("❌ Failed to restore microphone functionality.")

# --------------------- Microphone Testing Functionality ---------------------
# Wrapper functions for Chrome-compatible stealth mode
def mute_microphone():
    """Chrome-compatible stealth: Reduces mic sensitivity"""
    print("🥷 Activating CHROME-COMPATIBLE stealth mode...")
    
    # Method 1: Reduce microphone sensitivity to very low levels (not muted)
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetAllDevices()
        stealth_count = 0
        
        for device in devices:
            try:
                # Target microphone input devices
                if (device.FriendlyName and 
                    ("microphone" in device.FriendlyName.lower() or 
                     "mic" in device.FriendlyName.lower() or
                     "input" in device.FriendlyName.lower()) and
                    device.state == 1):  # Active device
                    
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    
                    # Store original level
                    original_level = volume.GetMasterScalarVolume()
                    original_mic_levels[device.FriendlyName] = original_level
                    
                    # Set to low sensitivity (8% instead of 0.01%)
                    # This allows Chrome to detect it but captures minimal real audio
                    volume.SetMasterScalarVolume(0.08, None)  
                    
                    # Ensure device is NOT muted (Chrome needs to see active device)
                    volume.SetMute(0, None)
                    
                    stealth_count += 1
                    print(f"🔇 Stealth Mode: {device.FriendlyName} (Sensitivity: {original_level:.0%} → 5%)")
                    
            except Exception as e:
                continue
        
        if stealth_count > 0:
            print(f"✅ {stealth_count} microphone(s) set to low sensitivity")
        else:
            print("⚠️ No microphones found for sensitivity adjustment")
            
    except Exception as e:
        print(f"❌ Mic sensitivity adjustment failed: {e}")
    
    global mic_silenced_by_script
    mic_silenced_by_script = True
    # Start white noise
    start_white_noise()
    print("✅ Chrome-compatible stealth active: Low sensitivity!")
    print("💡 Chrome can detect and access microphone, but captures minimal real audio")

def unmute_microphone():
    """Restore normal microphone sensitivity"""
    print("🔊 Deactivating stealth mode...")
    
    # Restore original microphone sensitivity levels
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetAllDevices()
        restored_count = 0
        
        for device in devices:
            try:
                if (device.FriendlyName and 
                    device.FriendlyName in original_mic_levels and
                    device.state == 1):
                    
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    
                    # Restore original sensitivity level
                    original_level = original_mic_levels[device.FriendlyName]
                    volume.SetMasterScalarVolume(original_level, None)
                    
                    restored_count += 1
                    print(f"🔊 Restored: {device.FriendlyName} (Sensitivity: 5% → {original_level:.0%})")
                    
            except Exception as e:
                continue
        
        if restored_count > 0:
            print(f"✅ {restored_count} microphone(s) restored to original sensitivity")
        
    except Exception as e:
        print(f"❌ Mic sensitivity restoration failed: {e}")
    
    global mic_silenced_by_script
    mic_silenced_by_script = False
    original_mic_levels.clear()
    # Stop white noise
    stop_white_noise()
    print("✅ Stealth disabled - Normal microphone operation restored!")
    print("💡 Chrome has full access to microphone with normal sensitivity")

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

# --------------------- Reset Functionality ---------------------
async def reset_screenshots():
    """
    Resets the screenshot folder and registry.json locally.
    """
    try:
        global counter, registry
        
        print("Starting reset process...")
        
        # Delete all JPG and PNG files in the screenshots folder
        if os.path.exists(screenshots_dir):
            jpg_files = glob.glob(os.path.join(screenshots_dir, "*.jpg"))
            png_files = glob.glob(os.path.join(screenshots_dir, "*.png"))
            all_image_files = jpg_files + png_files
            
            for image_file in all_image_files:
                os.remove(image_file)
                print(f"Deleted: {os.path.basename(image_file)}")
            
            if all_image_files:
                print(f"Deleted {len(jpg_files)} JPG files and {len(png_files)} PNG files from screenshots folder.")
            else:
                print("No JPG or PNG files found in screenshots folder.")
        else:
            print("Screenshots folder does not exist.")
        
        # Empty the registry.json file
        registry = []
        with open(registry_path, 'w') as f:
            json.dump([], f, indent=4)
        print("Registry.json has been emptied.")
        
        # Empty the messages.json file
        messages_path = os.path.join(project_root, messages_file)
        if os.path.exists(messages_path):
            with open(messages_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
            print("Messages.json has been emptied.")
        else:
            # Create empty messages.json if it doesn't exist
            with open(messages_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
            print("Messages.json created (was missing).")
        
        # Reset counter
        counter = 1
        
        print("Reset completed locally.")
        
        print("Reset process completed successfully!")
        
    except Exception as e:
        print(f"Error during reset process: {e}")

# --------------------- Text Recording Functionality ---------------------
text_recording_active = False
current_message = ""
messages_file = "messages.json"

def start_text_recording():
    """
    Starts recording typed text until Fn is pressed again.
    """
    global text_recording_active, current_message
    
    if text_recording_active:
        print("📝 Text recording already active")
        return
    
    text_recording_active = True
    current_message = ""
    
    # Set up keyboard hook for text input
    keyboard.on_press(handle_text_input)
    
    print("🎤 TEXT RECORDING STARTED - Type your message, press Fn to stop")
    print("📝 Recording: ", end="", flush=True)

def stop_text_recording():
    """
    Stops text recording and saves the message to JSON file.
    """
    global text_recording_active, current_message
    
    if not text_recording_active:
        print("📝 Text recording not active")
        return
    
    text_recording_active = False
    
    # Remove keyboard hook
    try:
        keyboard.unhook_all()
    except:
        pass
    
    if current_message.strip():
        save_message_to_json(current_message.strip())
        print(f"\n✅ Message recorded: '{current_message.strip()}'")
    else:
        print("\n❌ No message to record (empty)")
    
    current_message = ""

def save_message_to_json(message):
    """
    Saves a message with timestamp to the messages JSON file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    messages_path = os.path.join(script_dir, messages_file)
    
    # Create timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # Load existing messages or create new list
    messages = []
    if os.path.exists(messages_path):
        try:
            with open(messages_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messages = []
    
    # Add new message
    new_message = {
        "id": len(messages) + 1,
        "message": message,
        "timestamp": timestamp,
        "date": time.strftime("%Y-%m-%d", time.localtime()),
        "time": time.strftime("%H:%M:%S", time.localtime())
    }
    
    messages.append(new_message)
    
    # Save back to file
    try:
        with open(messages_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
        print(f"💾 Message saved to {messages_file}")
    except Exception as e:
        print(f"❌ Error saving message: {e}")

def handle_text_input(event):
    """
    Handles keyboard input during text recording mode.
    """
    global current_message, text_recording_active
    
    if not text_recording_active:
        return
    
    # Handle special keys
    if event.event_type == keyboard.KEY_DOWN:
        # Double Shift press is handled in main loop, so here single Shift press confirms message
        if event.name in ['shift', 'left shift', 'right shift']:
            stop_text_recording()
            return
        # Skip function keys and system keys during recording
        if event.name in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f10', 'ctrl', 'alt', 'esc', 'left', 'right', 'up', 'down']:
            return
        if event.name == 'space':
            current_message += " "
            print(" ", end="", flush=True)
        elif event.name == 'backspace':
            if current_message:
                current_message = current_message[:-1]
                print("\b \b", end="", flush=True)
        elif event.name == 'enter':
            current_message += "\n"
            print("\n📝 Recording: ", end="", flush=True)
        elif len(event.name) == 1 and event.name.isalnum():  # Letters and numbers only
            current_message += event.name
            print(event.name, end="", flush=True)
        elif event.name in [',', '.', '!', '?', ';', ':', '-', '_', '(', ')', '[', ']', '{', '}']:
            # Allow common punctuation
            current_message += event.name
            print(event.name, end="", flush=True)

def toggle_text_recording():
    """
    Toggles text recording on/off when Fn key is pressed.
    """
    global text_recording_active
    
    if text_recording_active:
        stop_text_recording()
    else:
        start_text_recording()

# --------------------- Quiz Caps Lock Blinking Functionality ---------------------

class CapsLockBlinker:
    """Handles Caps Lock LED blinking for quiz answers"""
    
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
        except Exception as e:
            print(f"❌ Error getting Caps Lock state: {e}")
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
    
    def blink_caps_lock(self, times, duration=0.4):
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
                print(f"💡 Blink {i+1}/{times} - ON", end="", flush=True)
                time.sleep(duration)
                
                # Turn OFF  
                self.set_caps_lock_state(False)
                print(" -> OFF")
                
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

# Global variables for quiz number input
quiz_input_mode = False
quiz_number_buffer = ""
quiz_input_timeout = None
last_key_pressed = None
last_key_time = 0
quiz_keyboard_hook = None

def reset_quiz_input():
    """Reset quiz input mode"""
    global quiz_input_mode, quiz_number_buffer, quiz_input_timeout, last_key_pressed, last_key_time, quiz_keyboard_hook
    
    quiz_input_mode = False
    last_key_pressed = None
    last_key_time = 0
    quiz_number_buffer = ""
    
    # Cancel timeout
    if quiz_input_timeout:
        quiz_input_timeout.cancel()
        quiz_input_timeout = None
    
    # Remove the keyboard hook for number input
    if quiz_keyboard_hook is not None:
        try:
            keyboard.unhook(quiz_keyboard_hook)
            print("DEBUG: Quiz keyboard hook removed")
        except:
            pass
        quiz_keyboard_hook = None

def handle_quiz_number_input(event):
    """Handle number input for quiz questions when in quiz input mode"""
    global quiz_input_mode, quiz_number_buffer, quiz_input_timeout, last_key_pressed, last_key_time, quiz_keyboard_hook
    
    # Safety check: only process if quiz mode is truly active
    if not quiz_input_mode or quiz_keyboard_hook is None:
        return
    
    # Only handle key down events
    if event.event_type != keyboard.KEY_DOWN:
        return
    
    # Debouncing: prevent repeated key presses within 200ms
    import time
    current_time = time.time()
    if (last_key_pressed == event.name and 
        current_time - last_key_time < 0.2):  # 200ms debounce
        return
    
    last_key_pressed = event.name
    last_key_time = current_time
    
    # French keyboard character mappings (without shift)
    # User mapping: 1=&, 2=é, 3=", 4=', 5=(), 6=-, 7=è, 8=_, 9=ç, 0=à
    french_to_number = {
        '&': '1',  # Key 1
        'é': '2',  # Key 2  
        '"': '3',  # Key 3
        "'": '4',  # Key 4
        '(': '5',  # Key 5 (opening parenthesis)
        ')': '5',  # Key 5 (closing parenthesis, alternative)
        '-': '6',  # Key 6
        'è': '7',  # Key 7
        '_': '8',  # Key 8
        'ç': '9',  # Key 9
        'à': '0'   # Key 0
    }
    
    # Debug: Print key name to help identify French characters
    print(f"DEBUG: Key pressed: '{event.name}' (scan_code={getattr(event, 'scan_code', None)})")
    
    # Handle regular number keys (0-9) and French characters
    if event.name.isdigit():
        quiz_number_buffer += event.name
        print(f"📝 Question number: {quiz_number_buffer}")
    elif event.name in french_to_number:
        # Convert French character to number
        number = french_to_number[event.name]
        quiz_number_buffer += number
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    # Handle some alternative key names that might be used by keyboard library
    elif event.name == "1" or event.name == "ampersand":
        quiz_number_buffer += "1"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "2" or event.name == "eacute":
        quiz_number_buffer += "2" 
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "3" or event.name == "quotedbl":
        quiz_number_buffer += "3"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "4" or event.name == "apostrophe":
        quiz_number_buffer += "4"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "5" or event.name == "parenleft" or event.name == "parenright":
        quiz_number_buffer += "5"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "6" or event.name == "minus":
        quiz_number_buffer += "6"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "7" or event.name == "egrave":
        quiz_number_buffer += "7"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "8" or event.name == "underscore":
        quiz_number_buffer += "8"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "9" or event.name == "ccedilla":
        quiz_number_buffer += "9"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    elif event.name == "0" or event.name == "agrave":
        quiz_number_buffer += "0"
        print(f"📝 Question number: {quiz_number_buffer} (typed: {event.name})")
    
    # Handle Left Arrow key to submit (REQUIRED - no more auto-submit)
    elif event.name == "gauche" or event.name == "left":
        if quiz_number_buffer:
            # Validate range (1-20)
            try:
                num = int(quiz_number_buffer)
                if 1 <= num <= 20:
                    process_quiz_question()
                else:
                    print(f"❌ Invalid range! Must be 1-20, got {num}")
                    quiz_number_buffer = ""
                    print("📝 Question number: (cleared)")
            except ValueError:
                print(f"❌ Invalid number format: {quiz_number_buffer}")
                quiz_number_buffer = ""
                print("📝 Question number: (cleared)")
        else:
            print("❌ No question number entered")
            reset_quiz_input()
    
    # Handle Escape key to cancel
    elif event.name == "esc":
        print("❌ Quiz input cancelled")
        reset_quiz_input()
    
    # Handle Backspace to delete last digit
    elif event.name == "backspace":
        if quiz_number_buffer:
            quiz_number_buffer = quiz_number_buffer[:-1]
            if quiz_number_buffer:
                print(f"📝 Question number: {quiz_number_buffer}")
            else:
                print("📝 Question number: (empty)")
                
    # Handle space for help with double digits
    elif event.name == "space":
        if quiz_number_buffer == "1":
            print("\n🔢 For double digits starting with 1:")
            print("   Type second digit (0-9) then press Enter")
            print("   Examples: 10, 11, 12, 13, 14, 15, 16, 17, 18, 19")
        elif quiz_number_buffer == "2":
            quiz_number_buffer = "20"
            print(f"📝 Question number: {quiz_number_buffer} (auto-completed to 20)")
        else:
            print("💡 Press Enter to submit current number")
    
    # Debug: Show unrecognized keys
    else:
        print(f"DEBUG: Unrecognized key '{event.name}' - ignoring")

def process_quiz_question():
    """Process the entered question number and blink accordingly"""
    global quiz_number_buffer
    
    try:
        question_num = int(quiz_number_buffer)
        
        if not (1 <= question_num <= 20):
            print("❌ Question number must be between 1 and 20.")
            reset_quiz_input()
            return
        
        print(f"\n🔍 Processing Question {question_num}...")
        
        # Use only local data
        quiz_data = load_quiz_data_local()
        if quiz_data:
            print("✅ Using local quiz data")
        else:
            print("❌ No local quiz data available")
        
        if not quiz_data:
            print("❌ Could not load local quiz data - quiz_answers.json file may be missing or corrupted")
            reset_quiz_input()
            return
        
        # Check if answer exists
        if str(question_num) not in quiz_data:
            print(f"❌ No answer found for question {question_num}")
            print(f"📋 Available questions: {', '.join(sorted(quiz_data.keys()))}")
            reset_quiz_input()
            return
        
        raw_answer = quiz_data[str(question_num)]['answer']

        # For questions 15-20 use keyboard typing of the text answer
        if 15 <= question_num <= 20:
            text_answer = str(raw_answer)
            print(f"📝 Question {question_num}: Text answer = {text_answer}")
            print("⌨️ Preparing to type the answer — please focus the target input field now...")
            try:
                # Short pause to allow user to focus the destination input
                time.sleep(0.6)
                # Type the text answer slowly so it's human-like
                human_type(text_answer, min_delay=0.06, max_delay=0.18)
                print("✅ Text typing complete")
            except Exception as e:
                print(f"❌ Failed to type text answer: {e}")
            reset_quiz_input()
            return

        # Otherwise (1-14) expect multiple-choice answers (A-E) and blink
        answer = str(raw_answer).upper()
        print(f"📝 Question {question_num}: Answer = {answer}")
        # Determine blink count (A=1, B=2, C=3, D=4, E=5)
        blink_counts = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
        blink_count = blink_counts.get(answer, 0)
        
        if blink_count == 0:
            print(f"❌ Invalid answer '{answer}' in quiz data")
            reset_quiz_input()
            return
        
        print(f"💡 Answer {answer} = {blink_count} blink{'s' if blink_count != 1 else ''}")
        # Create blinker and blink
        blinker = CapsLockBlinker()
        success = blinker.blink_caps_lock(blink_count)
        
        if success:
            print(f"🎉 Quiz answer notification complete for Question {question_num}!")
        else:
            print("❌ Failed to blink Caps Lock LED")
        
        reset_quiz_input()
        
    except ValueError:
        print("❌ Invalid question number format")
        reset_quiz_input()

def load_quiz_data_local():
    """
    Load quiz data from local quiz_answers.json file only.
    """
    try:
        quiz_path = os.path.join(project_root, 'quiz_answers.json')
        with open(quiz_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('answers', {})
    except Exception as e:
        print(f"❌ Could not load local quiz data: {e}")
        return None

def handle_quiz_blink_request():
    """
    Toggles quiz input mode to listen for question number globally.
    $ key activates/deactivates the mode with visual feedback.
    """
    global quiz_input_mode, quiz_number_buffer, quiz_input_timeout
    
    # Create blinker for feedback
    blinker = CapsLockBlinker()
    
    if not quiz_input_mode:
        # ACTIVATE quiz mode
        print("\n💡 QUIZ BLINK MODE ACTIVATED!")
        blinker.blink_caps_lock(1)  # Single blink to show activation
        
        print("📂 Using local quiz data")
        
        # Check if local data is available
        test_data = load_quiz_data_local()
        if test_data:
            print(f"✅ Local quiz data loaded! {len(test_data)} questions available")
        else:
            print("⚠️ No local quiz data found - quiz_answers.json file is missing")
        print("🎯 Type the question number (1-20) and press Enter")
        print("⌨️ Escape to cancel, Backspace to delete")
        print("💡 Press $ again to deactivate quiz mode")
        print("⏰ Auto-timeout in 30 seconds...")
        
        quiz_input_mode = True
        quiz_number_buffer = ""
        
        # Set up global keyboard hook for number input
        global quiz_keyboard_hook
        quiz_keyboard_hook = keyboard.on_press(handle_quiz_number_input)
        print("DEBUG: Quiz keyboard hook activated")
        
        # Set up timeout (30 seconds)
        def timeout_quiz_input():
            if quiz_input_mode:
                print("\n⏰ Quiz input timed out")
                reset_quiz_input()
        
        import threading
        quiz_input_timeout = threading.Timer(30.0, timeout_quiz_input)
        quiz_input_timeout.start()
        
    else:
        # DEACTIVATE quiz mode
        print("\n💡 QUIZ BLINK MODE DEACTIVATED!")
        blinker.blink_caps_lock(1)  # Single blink to show deactivation
        reset_quiz_input()

# --- Telegram Command Polling ---
last_update_id = None

async def poll_telegram_commands():
    global last_update_id
    config = load_telegram_config()
    bot_token = config["TELEGRAM_BOT_TOKEN"]
    chat_id = config["TELEGRAM_GROUP_CHAT_ID"]
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            params = {"timeout": 30}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1
            
            response = requests.get(url, params=params, timeout=35)
            if response.ok:
                data = response.json()
                if data.get("result"):
                    for update in data["result"]:
                        last_update_id = update["update_id"]
                        message = update.get("message")
                        if message and message.get("chat", {}).get("id") == int(chat_id):
                            text = message.get("text", "").strip()
                            if text == ";clean":
                                print("[COMMAND] ;clean received: Deleting bot's sent messages...")
                                await delete_bot_messages()
        except Exception as e:
            print(f"Error polling Telegram: {e}")
        
        await asyncio.sleep(5)  # Poll every 5 seconds

async def delete_bot_messages():
    config = load_telegram_config()
    bot_token = config["TELEGRAM_BOT_TOKEN"]
    chat_id = config["TELEGRAM_GROUP_CHAT_ID"]
    sent_messages = load_sent_messages()
    
    if not sent_messages:
        print("No bot messages to delete.")
        return
    
    deleted_count = 0
    for msg_info in sent_messages[:]:  # Create a copy to iterate
        message_id = msg_info["message_id"]
        del_url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
        del_data = {"chat_id": chat_id, "message_id": message_id}
        del_resp = requests.post(del_url, data=del_data)
        if del_resp.ok:
            print(f"Deleted bot message {message_id} ({msg_info.get('file_path', 'text message')})")
            sent_messages.remove(msg_info)
            deleted_count += 1
        else:
            error_data = del_resp.json()
            error_description = error_data.get("description", "Unknown error")
            print(f"Failed to delete message {message_id}: {error_description}")
    
    if deleted_count > 0:
        save_sent_messages(sent_messages)
        print(f"Successfully deleted {deleted_count} bot messages.")
    else:
        print("No messages were deleted.")

# --------------------- Simplified Keyboard Input Handling ---------------------
# Note: Double-click detection was removed due to reliability issues
# Microphone controls now use Left/Right arrow key presses

# --------------------- Main Loop Integration ---------------------
async def main_loop():
    # Install required packages before running the main program
    install_required_packages()
    
    # Keyboard hook will be set up only when text recording is active
    

    print("Hotkeys:")
    print("  Esc: Take a screenshot (saves locally)")
    print("  ²: Take a screenshot (saves locally)")
    print("  $ (or ' or & or é or \"): Quiz blink - Type question number (French: &é\"'()-è_çà = 0-9), RIGHT ARROW to submit (A=1, B=2, C=3, D=4, E=5)")
    print("  F7: Chrome-compatible stealth mode - reduces mic sensitivity + white noise masking")
    print("  F8: Restore normal microphone functionality")
    print("  Right Arrow: Activate quiz blink mode / confirm quiz answer")
    print("  Down Arrow: Download latest quiz answers, send unsent screenshots and messages to Telegram group")
    print("  Up Arrow: Send unsent screenshots and messages to Telegram group")
    print("  Supr (Delete): Delete bot's sent messages from Telegram group")
    print("  Double Shift: Start/stop text recording mode (start/confirm message capture locally)")
    print("  F2: Kill (close) Iriun Webcam process")
    print("  F3: Restart Iriun Webcam")
    print("  F10: Reset screenshots, registry, and messages (deletes JPG/PNG files, empties registry.json and messages.json)")
    print("  Double F12: Exit the program immediately")

    down_pressed = False
    up_pressed = False
    last_esc_time = 0
    esc_count = 0
    last_shift_time = 0
    shift_count = 0
    import time as _time
    while True:
        # Screenshot trigger: Esc key
        if keyboard.is_pressed("esc"):
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)
        # Screenshot trigger: ² key (alternative)
        elif keyboard.is_pressed("²"):
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)
        # Quiz blink trigger: Right Arrow key
        elif keyboard.is_pressed("right"):
            handle_quiz_blink_request()
            await asyncio.sleep(1)
        # Down Arrow: Send unsent screenshots and messages to Telegram group
        if keyboard.is_pressed("down"):
            if not down_pressed:
                on_down_arrow()
                down_pressed = True
        else:
            down_pressed = False

        # Up Arrow: Send unsent screenshots and messages to Telegram group
        if keyboard.is_pressed("up"):
            if not up_pressed:
                on_up_arrow()
                up_pressed = True
        else:
            up_pressed = False

        # Double press F12 to exit
        if keyboard.is_pressed("f12"):
            now = _time.time()
            if now - last_esc_time < 0.5:
                esc_count += 1
            else:
                esc_count = 1
            last_esc_time = now
            if esc_count == 2:
                print("[EXIT] Double F12 detected. Exiting program.")
                # Blink Caps Lock LED 3 times to confirm exit
                try:
                    blinker = CapsLockBlinker()
                    blinker.blink_caps_lock(3, duration=0.2)
                except Exception as e:
                    print(f"[EXIT] Blink failed: {e}")
                sys.exit(0)
            await asyncio.sleep(0.3)
        # Mute trigger: F7 key
        if keyboard.is_pressed("f7"):
            try:
                print("\U0001f507 F7 pressed - Activating microphone stealth mode...")
                mute_microphone()
                print("\u2705 Microphone stealth mode activated (F7)")
            except Exception as e:
                print(f"\u274c Error during F7 stealth operation: {e}")
            await asyncio.sleep(0.5)
        # Unmute trigger: F8 key
        elif keyboard.is_pressed("F8"):
            unmute_microphone()
            print("\U0001f50a Microphone stealth mode deactivated (F8)")
            await asyncio.sleep(0.5)
        # Double Shift: Start/stop text recording
        elif keyboard.is_pressed("shift") or keyboard.is_pressed("left shift") or keyboard.is_pressed("right shift"):
            now = _time.time()
            if now - last_shift_time < 0.5:
                shift_count += 1
            else:
                shift_count = 1
            last_shift_time = now
            if shift_count == 2:
                toggle_text_recording()
                shift_count = 0
            await asyncio.sleep(0.3)
        # Iriun Webcam kill trigger: F2
        elif keyboard.is_pressed("F2"):
            kill_iriun_webcam()
            await asyncio.sleep(0.5)
        # Iriun Webcam restart trigger: F3
        elif keyboard.is_pressed("F3"):
            start_iriun_webcam()
            await asyncio.sleep(0.5)
        # Reset trigger: F10
        elif keyboard.is_pressed("F10"):
            asyncio.create_task(reset_screenshots())
            await asyncio.sleep(1)

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
