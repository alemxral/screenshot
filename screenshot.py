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
import requests
import base64
import ctypes
from ctypes import wintypes

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
    
    try:
        import numpy
        import sounddevice
        print("Package 'numpy' and 'sounddevice' are already installed.")
    except ImportError:
        missing_packages.append('numpy')
        missing_packages.append('sounddevice')
    
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
        # Pull latest changes first
        print("⬇️ Pulling latest changes...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "pull", "--rebase",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        print(" ✅" if proc.returncode == 0 else " ⚠️")
        
        # Add files
        proc = await asyncio.create_subprocess_exec(
            "git", "add", filepath, registry_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        # Commit
        commit_message = f"Add screenshot {filename} and update registry"
        proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", commit_message,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        # Force push
        proc = await asyncio.create_subprocess_exec(
            "git", "push", "--force-with-lease", "origin", "main",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(f"✅ Screenshot {filename} force-pushed to git.")
        else:
            # Try regular force push
            proc = await asyncio.create_subprocess_exec(
                "git", "push", "--force", "origin", "main",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            print(f"✅ Screenshot {filename} force-pushed to git (regular force).")
            
    except Exception as e:
        print("Git push error:", e)

def async_git_push(filepath, filename):
    # Launch a daemon thread that runs an asyncio event loop to push to git.
    threading.Thread(target=lambda: asyncio.run(git_push(filepath, filename)), daemon=True).start()

async def batch_git_push():
    """
    Performs batch git operations: add all changes, commit, and force push.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("🔄 Starting batch git operations...")
        
        # Pull latest changes first
        print("⬇️ Pulling latest changes from remote...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "pull", "--rebase",
            cwd=script_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
        else:
            print(" ⚠️ (Pull failed, continuing anyway)")
        
        # Add all changes
        print("📝 Adding all changes to git staging area...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "add", ".",
            cwd=script_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
        else:
            print(f" ❌ (Error: {stderr.decode().strip()})")
            raise Exception(f"Git add failed: {stderr.decode().strip()}")
        
        # Commit changes
        import datetime
        commit_message = f"Batch update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print("📝 Committing changes to git...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", commit_message,
            cwd=script_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
        else:
            # Check if it's just "nothing to commit" (not an error)
            stderr_text = stderr.decode().strip()
            if "nothing to commit" in stderr_text or "no changes added" in stderr_text:
                print(" ⏭️ (No changes to commit)")
                
                # Still provide confirmation feedback for "no changes" case
                try:
                    import winsound
                    winsound.Beep(600, 200)  # Lower tone, shorter beep for "no changes"
                    
                    blinker = CapsLockBlinker()
                    blinker.blink_caps_lock(1)  # Single blink for "no changes"
                    
                    print("🔔 No changes confirmation: beep + caps lock blink")
                except Exception as confirm_error:
                    print(f"⚠️ Confirmation failed: {confirm_error}")
                return
            else:
                print(f" ❌ (Error: {stderr_text})")
                raise Exception(f"Git commit failed: {stderr_text}")
        
        # Force push to remote repository
        print("🚀 Force pushing to remote repository...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "push", "--force", "origin", "main",
            cwd=script_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
            print("🎉 All changes successfully force-pushed to remote repository!")
            
            # Success confirmation: beep and caps lock blink
            try:
                # System beep (Windows)
                import winsound
                winsound.Beep(800, 300)  # 800 Hz for 300ms
                
                # Caps lock blink confirmation
                blinker = CapsLockBlinker()
                blinker.blink_caps_lock(2)  # Double blink for success
                
                print("🔔 Success confirmation: beep + caps lock blink")
            except Exception as confirm_error:
                print(f"⚠️ Confirmation failed: {confirm_error}")
        else:
            print(f" ❌ (Error: {stderr.decode().strip()})")
            raise Exception(f"Git force push failed: {stderr.decode().strip()}")
        
    except Exception as e:
        print(f"\n⚠️ Batch git operations failed: {e}")
        print("🔧 Try running 'git status' to check repository state")

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
                    
                    # Set INPUT capture level to low but active (0.02 = 2% sensitivity)
                    volume.SetMasterScalarVolume(0.02, None)  # Low input sensitivity but still active
                    
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
            result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command], 
                         capture_output=True, text=True, check=False)
            
            # Only show success if there were no errors
            if result.returncode == 0:
                print("🔇 Microphone INPUT sensitivity minimized via PowerShell")
                mic_silenced_by_script = True
                success = True
            else:
                print(f"PowerShell command returned error code: {result.returncode}")
                if result.stderr:
                    print(f"PowerShell error: {result.stderr}")
                    
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

# --------------------- White Noise Generation ---------------------
white_noise_thread = None
white_noise_active = False

def generate_white_noise():
    """
    Generates continuous white noise to inject into microphone input.
    This makes the microphone appear active while masking real audio.
    """
    global white_noise_active
    
    try:
        import numpy as np
        import sounddevice as sd
        
        # Audio parameters for realistic background noise
        sample_rate = 44100  # Standard sample rate
        duration = 50 # Generate in small chunks for continuous stream
         
        print("🔊 Starting white noise injection...")
        
        while white_noise_active:
            # Generate low-level white noise (very quiet background)
            noise_amplitude = 0.02  # Very low volume (2% of max)
            white_noise = np.random.normal(0, noise_amplitude, int(sample_rate * duration))
            
            # Apply slight filtering to make it sound more natural
            # Add some pink noise characteristics (more bass, less treble)
            for i in range(1, len(white_noise)):
                white_noise[i] = white_noise[i] * 0.8 + white_noise[i-1] * 0.2
            
            try:
                # Play through default input device (microphone injection)
                sd.play(white_noise, samplerate=sample_rate, device=None, blocking=False)
                time.sleep(duration * 0.9)  # Small overlap for seamless audio
            except Exception as play_error:
                # If direct injection fails, continue generating for CPU/detection purposes
                time.sleep(duration)
                
    except Exception as e:
        print(f"White noise generation error: {e}")
        print("📝 Install sounddevice: pip install sounddevice numpy")

def start_white_noise():
    """
    Starts white noise injection in background thread.
    """
    global white_noise_thread, white_noise_active
    
    if white_noise_active:
        print("🔊 White noise already active")
        return
    
    white_noise_active = True
    white_noise_thread = threading.Thread(target=generate_white_noise, daemon=True)
    white_noise_thread.start()
    print("🎵 White noise injection started - microphone appears naturally active!")

def stop_white_noise():
    """
    Stops white noise injection.
    """
    global white_noise_active
    
    if white_noise_active:
        white_noise_active = False
        print("🔇 White noise injection stopped")
    else:
        print("🔇 White noise already inactive")

def enhanced_silent_mute_microphone():
    """
    Enhanced stealth mute: Reduces microphone sensitivity AND adds white noise.
    Perfect stealth - apps see active microphone with 'natural' background noise.
    """
    try:
        print("🥷 Activating ENHANCED stealth mode...")
        print("DEBUG: About to call silent_mute_microphone()")
        silent_mute_microphone()  # Reduce input sensitivity
        print("DEBUG: About to call start_white_noise()")
        start_white_noise()       # Add fake background noise
        print("✅ Enhanced stealth active: Low sensitivity + White noise masking!")
    except Exception as e:
        print(f"❌ Error in enhanced_silent_mute_microphone: {e}")

def enhanced_silent_unmute_microphone():
    """
    Disables enhanced stealth mode and restores normal microphone operation.
    """
    print("🔊 Deactivating enhanced stealth mode...")
    stop_white_noise()         # Stop white noise first
    silent_unmute_microphone() # Restore normal sensitivity
    print("✅ Enhanced stealth disabled - microphone fully restored!")

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

# Wrapper functions for Chrome-compatible stealth mode
def mute_microphone():
    """Chrome-compatible stealth: Reduces mic sensitivity + adds white noise masking"""
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
    
    # Method 2: Add white noise masking for extra stealth
    start_white_noise()
    
    global mic_silenced_by_script
    mic_silenced_by_script = True
    print("✅ Chrome-compatible stealth active: Low sensitivity + White noise masking!")
    print("💡 Chrome can detect and access microphone, but captures minimal real audio")

def unmute_microphone():
    """Restore normal microphone sensitivity and disable white noise"""
    print("🔊 Deactivating stealth mode...")
    
    # Stop white noise first
    stop_white_noise()
    
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
        # Use async version to save and push to git
        asyncio.create_task(save_message_async(current_message.strip()))
        print(f"\n✅ Message recorded: '{current_message.strip()}'")
        print("🚀 Pushing message to git repository...")
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

async def save_message_async(message):
    """
    Saves a message to JSON file locally.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    messages_path = os.path.join(script_dir, messages_file)
    project_root = script_dir
    
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
        return
    
    print("✅ Message saved locally")

def handle_text_input(event):
    """
    Handles keyboard input during text recording mode and special vibration trigger.
    """
    global current_message, text_recording_active
    
    # Handle vibration trigger with "!" key (works outside recording mode)
    if event.event_type == keyboard.KEY_DOWN and event.name == '!' and not text_recording_active:
        handle_vibration_request()
        return
    
    if not text_recording_active:
        return
    
    # Handle special keys
    if event.event_type == keyboard.KEY_DOWN:
        # Skip function keys and system keys during recording
        # Note: arrows are now used for microphone/git control - skip them in text recording
        # Note: esc is now used for screenshots - skip it in text recording
        if event.name in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f10', 'ctrl', 'shift', 'alt', 'esc', 'left', 'right', 'up', 'down']:
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

def handle_vibration_request():
    """
    Handles vibration request when "!" key is pressed.
    Prompts for question number and sends Telegram notification.
    """
    print("\n📱 VIBRATION REQUEST TRIGGERED!")
    question_num = input("Enter question number (1-20): ").strip()
    
    if not question_num.isdigit():
        print("❌ Invalid input. Must be a number.")
        return
        
    question_num = int(question_num)
    if not (1 <= question_num <= 20):
        print("❌ Question number must be between 1 and 20.")
        return
    
    # Call the Python vibration script
    try:
        import subprocess
        result = subprocess.run([sys.executable, "send_vibration.py", str(question_num)], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print(f"✅ Vibration notification sent for Question {question_num}!")
            print(result.stdout)
        else:
            print(f"❌ Error sending notification:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running vibration script: {e}")

def toggle_text_recording():
    """
    Toggles text recording on/off when Fn key is pressed.
    """
    global text_recording_active
    
    if text_recording_active:
        stop_text_recording()
    else:
        start_text_recording()

async def pull_latest_version():
    """
    Pull latest version from remote repository (Up Arrow key function)
    """
    print("\n⬇️ PULLING LATEST VERSION FROM REMOTE...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # First, show current status
        print("📋 Checking current repository status...")
        proc = await asyncio.create_subprocess_exec(
            "git", "status", "--short",
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if stdout.decode().strip():
            print("⚠️ You have local changes:")
            for line in stdout.decode().strip().split('\n'):
                print(f"   {line}")
            print("💾 Stashing local changes before pull...")
            
            # Stash local changes
            proc = await asyncio.create_subprocess_exec(
                "git", "stash", "push", "-m", "Auto-stash before pull (Up Arrow)",
                cwd=project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        
        # Pull latest changes
        print("⬇️ Pulling latest changes from origin/main...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "pull", "origin", "main",
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
            print("🎉 Successfully pulled latest version!")
            
            # Show what was updated
            if "Already up to date" in stdout.decode():
                print("📋 Repository was already up to date")
            else:
                print("📋 Updates received:")
                for line in stdout.decode().strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
        else:
            print(" ❌")
            print(f"❌ Pull failed: {stderr.decode().strip()}")
            
        # Restore stashed changes if any
        print("🔄 Checking for stashed changes to restore...")
        proc = await asyncio.create_subprocess_exec(
            "git", "stash", "list",
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if "Auto-stash before pull" in stdout.decode():
            print("📦 Restoring your local changes...")
            proc = await asyncio.create_subprocess_exec(
                "git", "stash", "pop",
                cwd=project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            print("✅ Local changes restored")
            
    except Exception as e:
        print(f"❌ Error during pull operation: {e}")

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

def load_quiz_data_from_github():
    """Load quiz data from GitHub repository"""
    url = "https://api.github.com/repos/alemxral/screenshot/contents/quiz_answers.json"
    
    try:
        print("📡 Requesting latest quiz data from GitHub API...", end="", flush=True)
        response = requests.get(url, timeout=15)  # Increased timeout
        
        if response.status_code == 200:
            print(" ✅ Response received")
            print("🔓 Decoding GitHub file content...", end="", flush=True)
            
            file_data = response.json()
            content = base64.b64decode(file_data['content']).decode('utf-8')
            quiz_data = json.loads(content)
            answers = quiz_data.get('answers', {})
            
            print(f" ✅ Done")
            print(f"📚 Successfully loaded {len(answers)} quiz answers from GitHub")
            
            # Show available questions
            if answers:
                question_list = ', '.join(sorted(answers.keys()))
                print(f"📋 Available questions: {question_list}")
            
            return answers
        else:
            print(f" ❌ HTTP Error {response.status_code}")
            if response.status_code == 404:
                print("📝 File not found - make sure quiz_answers.json exists in your repo")
            elif response.status_code == 403:
                print("🔒 Access denied - check repository permissions")
            elif response.status_code == 401:
                print("🔑 Authentication required - repo might be private")
            return None
            
    except requests.exceptions.Timeout:
        print(" ⏰ Timeout - GitHub is taking too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        print(" 🌐 Connection error - check your internet connection")
        return None
    except json.JSONDecodeError as e:
        print(f" ❌ JSON decode error: {e}")
        print("📝 The file might have invalid JSON format")
        return None
    except Exception as e:
        print(f" ❌ Unexpected error: {e}")
        return None

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
    print(f"DEBUG: Key pressed: '{event.name}'")
    
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
    
    # Handle Enter key to submit (REQUIRED - no more auto-submit)
    elif event.name == "enter":
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
            print("❌ Could not load local quiz data - Press Up Arrow to download from GitHub")
            reset_quiz_input()
            return
        
        # Check if answer exists
        if str(question_num) not in quiz_data:
            print(f"❌ No answer found for question {question_num}")
            print(f"📋 Available questions: {', '.join(sorted(quiz_data.keys()))}")
            reset_quiz_input()
            return
        
        answer = quiz_data[str(question_num)]['answer'].upper()
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
        with open('quiz_answers.json', 'r', encoding='utf-8') as f:
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
        
        print("📂 Using local quiz data (Press Up Arrow to fetch latest from GitHub)")
        
        # Check if local data is available
        test_data = load_quiz_data_local()
        if test_data:
            print(f"✅ Local quiz data loaded! {len(test_data)} questions available")
        else:
            print("⚠️ No local quiz data found - Press Up Arrow to download from GitHub first")
        
        print("🎯 Type the question number (1-20) from anywhere on your computer")
        print("🇫🇷 French keyboard: &é\"'()-è_çà = 1234567890")
        print("⌨️ PRESS ENTER to submit, Escape to cancel, Backspace to delete")
        print("🔢 For double digits (10-20): Type both digits then Enter")
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
    print("  $ (or ' or & or é or \"): Quiz blink - Type question number (French: &é\"'()-è_çà = 0-9), ENTER to submit (A=1, B=2, C=3, D=4, E=5)")
    print("  Left Arrow: Chrome-compatible stealth mode - reduces mic sensitivity + white noise masking")
    print("  Right Arrow: Restore normal microphone functionality")
    print("  Up Arrow: Pull latest version from GitHub (sync with remote)")
    print("  Down Arrow: Batch push all changes to git (add, commit, force push)")
    print("  F4: Toggle text recording mode (start/stop message capture locally)")
    print("  F1: Test microphone status and stealth mode")
    print("  F2: Kill (close) Iriun Webcam process")
    print("  F3: Restart Iriun Webcam")
    print("  F10: Reset screenshots, registry, and messages (deletes JPG/PNG files, empties registry.json and messages.json)")
    
    while True:
        # Screenshot trigger: Esc key
        if keyboard.is_pressed("esc"):
            # Create an asynchronous screenshot task.
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)  # Delay to avoid multiple triggers
        
        # Screenshot trigger: ² key (alternative)
        elif keyboard.is_pressed("²"):
            # Create an asynchronous screenshot task.
            asyncio.create_task(save_screenshot_async())
            await asyncio.sleep(1)  # Delay to avoid multiple triggers

        # Quiz blink trigger: ONLY $ key (shift+4)
        elif keyboard.is_pressed("shift+4") or keyboard.is_pressed("$"):
            handle_quiz_blink_request()
            await asyncio.sleep(1)  # Delay to avoid multiple triggers

        # Mute trigger: Left Arrow key
        if keyboard.is_pressed("left"):
            try:
                print("🔇 Left Arrow pressed - Activating microphone stealth mode...")
                mute_microphone()
                print("✅ Microphone stealth mode activated (Left Arrow)")
            except Exception as e:
                print(f"❌ Error during Left Arrow stealth operation: {e}")
            await asyncio.sleep(0.5)
        # Unmute trigger: Right Arrow key
        elif keyboard.is_pressed("right"):
            unmute_microphone()
            print("🔊 Microphone stealth mode deactivated (Right Arrow)")
            await asyncio.sleep(0.5)
        # Pull latest version: Up Arrow key
        elif keyboard.is_pressed("up"):
            await pull_latest_version()
            await asyncio.sleep(1)
        # Batch git push: Down Arrow key
        elif keyboard.is_pressed("down"):
            await batch_git_push()
            await asyncio.sleep(1)
        # Text recording toggle: F4 key
        elif keyboard.is_pressed("F4"):
            toggle_text_recording()
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
        # Reset trigger: F10
        elif keyboard.is_pressed("F10"):
            asyncio.create_task(reset_screenshots())
            await asyncio.sleep(1)

        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main_loop())
