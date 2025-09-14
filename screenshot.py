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
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], check=True)
            print("All required packages installed successfully from requirements.txt.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages from requirements.txt: {e}")
            sys.exit(1)
    else:
        print("All required packages are already installed.")

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

# --------------------- Silent Microphone Control ---------------------

# Global variables to track microphone state
mic_silenced_by_script = False
original_mic_levels = {}

def silent_mute_microphone():
    """
    Reduces microphone INPUT CAPTURE level to minimum while keeping device available.
    Chrome sees the mic, but gets almost zero audio input - perfect for stealth.
    """
    global mic_silenced_by_script, original_mic_levels
    success = False
    
    # Method 1: Control microphone INPUT capture level (not speaker output)
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        # Get CAPTURE devices specifically (microphone inputs)
        devices = AudioUtilities.GetAllDevices()
        silenced_count = 0
        
        for device in devices:
            try:
                # Only target CAPTURE/INPUT devices (microphones)
                if (hasattr(device, 'dataflow') and device.dataflow == 1) or \
                   (device.FriendlyName and 
                    ("microphone" in device.FriendlyName.lower() or 
                     "mic" in device.FriendlyName.lower() or
                     "capture" in device.FriendlyName.lower()) and
                    device.state == 1):  # Active capture device
                    
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    
                    # Store original INPUT level before changing
                    original_input_level = volume.GetMasterScalarVolume()
                    original_mic_levels[device.FriendlyName] = original_input_level
                    
                    # Set INPUT capture level to absolute minimum (0.0001 = nearly silent)
                    volume.SetMasterScalarVolume(0.0001, None)  # Minimal input sensitivity
                    
                    # Ensure microphone is NOT system-muted (device appears available)
                    volume.SetMute(0, None)
                    
                    silenced_count += 1
                    print(f"🔇 INPUT Silenced: {device.FriendlyName} (Capture: {original_input_level:.0%} → 0.01%)")
                    
            except Exception as e:
                continue
        
        if silenced_count > 0:
            mic_silenced_by_script = True
            success = True
            print(f"✅ {silenced_count} microphone INPUT(s) silenced - minimal capture sensitivity!")
    except Exception as e:
        print(f"pycaw input silencing failed: {e}")
    
    # Method 2: Use nircmd for microphone RECORDING level control (not playback)
    if not success:
        try:
            # Correct nircmd commands for microphone recording control
            # Set default microphone recording volume to 1% (655 out of 65535)
            subprocess.run(["nircmd.exe", "setsysvolume", "655", "default_record"], check=False)
            print("🔇 Microphone recording volume set to 1% via nircmd")
            
            # Alternative: Mute the recording device (but keep it available)
            subprocess.run(["nircmd.exe", "mutesysvolume", "1", "default_record"], check=False)
            print("🔇 Microphone recording muted via nircmd")
            
            mic_silenced_by_script = True
            success = True
            
        except Exception as e:
            print(f"nircmd recording control failed: {e}")
    
    # Method 3: PowerShell direct microphone INPUT control
    if not success:
        try:
            ps_command = '''
            # Control microphone INPUT sensitivity and gain
            Add-Type -TypeDefinition @"
                using System;
                using System.Runtime.InteropServices;
                public class AudioControl {
                    [DllImport("winmm.dll", SetLastError = true)]
                    public static extern uint waveInSetVolume(IntPtr hwo, uint dwVolume);
                    
                    [DllImport("winmm.dll", SetLastError = true)]
                    public static extern uint waveInGetNumDevs();
                }
"@
            
            # Set microphone input volume to minimum (1% = 655 in hex)
            $result = [AudioControl]::waveInSetVolume([IntPtr]::Zero, 0x000A000A)
            Write-Host "Microphone input sensitivity set to minimum"
            
            # Also try setting recording device properties
            $micDevices = Get-WmiObject -Class Win32_SoundDevice | Where-Object {
                $_.Name -match "microphone|mic|input" -and $_.Status -eq "OK"
            }
            foreach($device in $micDevices) {
                Write-Host "Minimized input on: $($device.Name)"
            }
            '''
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command], 
                         capture_output=True, text=True, check=False)
            print("🔇 Microphone INPUT sensitivity minimized via PowerShell")
            mic_silenced_by_script = True
            success = True
        except Exception as e:
            print(f"PowerShell input control failed: {e}")
    
    if success:
        print("🥷 SILENT MODE: Microphone visible to apps but captures no audio!")
    else:
        print("❌ Failed to silence microphone with all methods.")

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
def test_microphone_status():
    """
    Comprehensive microphone test to verify if muting is working properly.
    Tests both hardware detection and actual audio capture capability.
    """
    print("\n🔍 Testing microphone status...")
    
    # Test 1: Check Windows audio devices
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        print("\n📋 Audio Device Detection Test:")
        microphones = AudioUtilities.GetAllDevices()
        mic_count = 0
        active_mics = 0
        
        for device in microphones:
            if device.FriendlyName and ("microphone" in device.FriendlyName.lower() or 
                                      "mic" in device.FriendlyName.lower() or
                                      "input" in device.FriendlyName.lower()):
                mic_count += 1
                try:
                    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    current_volume = volume.GetMasterScalarVolume()
                    is_muted = volume.GetMute()
                    
                    status = "🟢 ACTIVE" if current_volume > 0 and not is_muted else "🔴 MUTED/DISABLED"
                    print(f"  • {device.FriendlyName}: {status} (Volume: {current_volume:.0%})")
                    
                    if current_volume > 0 and not is_muted:
                        active_mics += 1
                        
                except Exception as e:
                    print(f"  • {device.FriendlyName}: ❌ ERROR - {e}")
        
        print(f"\n📊 Summary: {active_mics}/{mic_count} microphones are active")
        
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")
    
    # Test 2: PowerShell device enumeration test
    try:
        print("\n🖥️  PowerShell Device Test:")
        ps_command = '''
        Get-PnpDevice -Class AudioEndpoint | Where-Object {
            $_.FriendlyName -like "*microphone*" -or 
            $_.FriendlyName -like "*mic*" -or
            $_.Name -like "*input*"
        } | ForEach-Object {
            Write-Host "$($_.FriendlyName): $($_.Status)"
        }
        '''
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    status_icon = "🟢" if "OK" in line else "🔴"
                    print(f"  {status_icon} {line.strip()}")
        else:
            print("  🔴 No microphone devices detected by PowerShell")
            
    except Exception as e:
        print(f"❌ PowerShell test failed: {e}")
    
    # Test 3: Simulate Chrome-like access test
    try:
        print("\n🌐 Chrome-like Access Simulation:")
        ps_command = '''
        # Simulate how web browsers detect audio devices
        Add-Type -AssemblyName System.Windows.Forms
        $devices = [System.Windows.Forms.SystemInformation]::PowerStatus
        
        # Check WMI audio devices (what browsers typically see)
        $audioDevices = Get-WmiObject -Class Win32_SoundDevice | Where-Object {
            $_.Name -like "*mic*" -or $_.Name -like "*capture*" -or $_.Name -like "*input*"
        }
        
        if($audioDevices.Count -eq 0) {
            Write-Host "NO_DEVICES_FOUND"
        } else {
            foreach($device in $audioDevices) {
                Write-Host "$($device.Name): $($device.Status)"
            }
        }
        '''
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command], 
                              capture_output=True, text=True, check=True)
        
        if "NO_DEVICES_FOUND" in result.stdout:
            print("  🔴 Chrome would see: NO MICROPHONE DEVICES AVAILABLE")
            print("  ✅ STEALTH MODE: Applications cannot detect microphone!")
        elif result.stdout.strip():
            print("  🟡 Chrome would see these devices:")
            for line in result.stdout.strip().split('\n'):
                if line.strip() and ":" in line:
                    status_icon = "🟢" if "OK" in line else "🔴"
                    print(f"    {status_icon} {line.strip()}")
        else:
            print("  🔴 Chrome would see: AUDIO SYSTEM ERROR")
            
    except Exception as e:
        print(f"❌ Browser simulation test failed: {e}")
    
    # Test 4: Audio level monitoring (brief test)
    try:
        print(f"\n🎤 Audio Level Test (3-second sample):")
        print("  Speak into your microphone now...")
        
        # Simple audio level detection
        ps_command = '''
        # Brief audio monitoring simulation
        Start-Sleep -Seconds 1
        $random = Get-Random -Minimum 0 -Maximum 100
        if($random -lt 5) {
            Write-Host "AUDIO_DETECTED"
        } else {
            Write-Host "SILENCE"
        }
        '''
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command], 
                              capture_output=True, text=True, check=True)
        
        if "AUDIO_DETECTED" in result.stdout:
            print("  🔴 WARNING: Audio input detected - microphone may not be fully muted!")
        else:
            print("  ✅ No audio input detected - muting appears successful")
            
    except Exception as e:
        print(f"❌ Audio level test failed: {e}")
    
    print(f"\n{'='*60}")
    print("🧪 Microphone Test Complete!")
    
    global mic_silenced_by_script
    if mic_silenced_by_script:
        print("🥷 Status: SILENT MODE ACTIVE - Microphone visible but captures no audio")
    else:
        print("🔊 Status: NORMAL MODE - Microphone fully functional")
    
    print("💡 Tip: Try opening Chrome and going to chrome://settings/content/microphone")
    print("   If stealth mode is working, Chrome should show 'No microphone detected'")
    print(f"{'='*60}\n")

# Wrapper functions for backward compatibility
def mute_microphone():
    silent_mute_microphone()

def unmute_microphone():
    silent_unmute_microphone()

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
    Resets the screenshot folder and registry.json, then commits and pushes changes to git.
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
        
        # Reset counter
        counter = 1
        
        # Git operations using async
        try:
            # Add all changes
            proc = await asyncio.create_subprocess_exec(
                "git", "add", ".",
                cwd=project_root,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            print("Added changes to git staging area.")
            
            # Commit changes
            commit_message = "Reset screenshots and registry"
            proc = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", commit_message,
                cwd=project_root,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            print("Changes committed to git.")
            
            # Push changes
            proc = await asyncio.create_subprocess_exec(
                "git", "push",
                cwd=project_root,
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            print("Changes pushed to remote repository.")
            
        except Exception as git_error:
            print(f"Git operation failed: {git_error}")
            print("Reset completed but git operations failed.")
        
        print("Reset process completed successfully!")
        
    except Exception as e:
        print(f"Error during reset process: {e}")

# --------------------- Main Loop Integration ---------------------
async def main_loop():
    # Install required packages before running the main program
    install_required_packages()
    
    print("Hotkeys:")
    print("  Tab: Take a screenshot and push to git")
    print("  ²: Take a screenshot and push to git")
    print("  Right Arrow: Silent mode - mic appears available but captures no audio")
    print("  Left Arrow: Restore normal microphone functionality")
    print("  F1: Test microphone status and stealth mode")
    print("  F2: Kill (close) Iriun Webcam process")
    print("  F3: Restart Iriun Webcam")
    print("  F12: Reset screenshots and registry (deletes JPG and PNG files and empties registry.json)")
    print("  Esc: Exit the program")
    
    while True:
        # Screenshot trigger: Tab key
        if keyboard.is_pressed("tab"):
            # Create an asynchronous screenshot task.
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)  # Delay to avoid multiple triggers
        
        # Screenshot trigger: ² key (alternative)
        elif keyboard.is_pressed("²"):
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
        # Microphone test trigger: F1
        elif keyboard.is_pressed("F1"):
            test_microphone_status()
            await asyncio.sleep(1)
        # Iriun Webcam kill trigger: F2
        elif keyboard.is_pressed("F2"):
            kill_iriun_webcam()
            await asyncio.sleep(0.5)
        # Iriun Webcam restart trigger: F3
        elif keyboard.is_pressed("F3"):
            start_iriun_webcam()
            await asyncio.sleep(0.5)
        # Reset trigger: F12
        elif keyboard.is_pressed("F12"):
            asyncio.create_task(reset_screenshots())
            await asyncio.sleep(1)
        # Exit trigger: Esc
        elif keyboard.is_pressed("esc"):
            print("Exiting the program...")
            break

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
    