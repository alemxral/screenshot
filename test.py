import subprocess
import keyboard
import os
import json
import glob
import sys
import time

def install_required_packages():
    """
    Auto-installs required packages from requirements.txt if not available.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(script_dir, "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print("requirements.txt file not found. Creating it...")
        with open(requirements_file, 'w') as f:
            f.write("keyboard==0.13.5\n")
    
    # Check if packages are installed by trying to import them
    missing_packages = []
    try:
        import keyboard
        print("Package 'keyboard' is already installed.")
    except ImportError:
        missing_packages.append('keyboard')
    
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

def kill_iriun_webcam():
    """
    Searches for processes with 'iriun' in their name and force-kills them.
    """
    try:
        # Run the 'tasklist' command and capture its output
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        process_found = False
        
        # Split the output into lines and search for 'iriun'
        for line in result.stdout.splitlines():
            if "iriun" in line.lower():
                # Assume the first token is the process name
                process_name = line.split()[0]
                print(f"Found process: {process_name}. Attempting to kill it...")
                # Force kill the process
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
    # Update the path to match your system:
    executable_path = r"C:\Program Files (x86)\Iriun Webcam\IriunWebcam.exe"
    
    if not os.path.exists(executable_path):
        print(f"Executable not found: {executable_path}")
        return
    
    try:
        # Use Popen to launch the process without blocking this script
        subprocess.Popen(executable_path, shell=True)
        print("Iriun Webcam has been restarted.")
    except Exception as e:
        print("Error starting Iriun Webcam:", e)

def reset_screenshots():
    """
    Resets the screenshot folder and registry.json, then commits and pushes changes to git.
    """
    try:
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        screenshots_dir = os.path.join(script_dir, "screenshots")
        registry_file = os.path.join(script_dir, "registry.json")
        
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
        if os.path.exists(registry_file):
            with open(registry_file, 'w') as f:
                json.dump([], f, indent=4)
            print("Registry.json has been emptied.")
        else:
            print("Registry.json file does not exist.")
        
        # Git operations
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=script_dir, check=True)
            print("Added changes to git staging area.")
            
            # Commit changes
            commit_message = "Reset screenshots and registry"
            subprocess.run(["git", "commit", "-m", commit_message], cwd=script_dir, check=True)
            print("Changes committed to git.")
            
            # Push changes
            subprocess.run(["git", "push"], cwd=script_dir, check=True)
            print("Changes pushed to remote repository.")
            
        except subprocess.CalledProcessError as git_error:
            print(f"Git operation failed: {git_error}")
            print("Reset completed but git operations failed.")
        
        print("Reset process completed successfully!")
        
    except Exception as e:
        print(f"Error during reset process: {e}")

def check_adb_connection():
    """
    Check if ADB is available and if there are connected Android devices.
    """
    try:
        # Check if ADB is available
        result = subprocess.run(["adb", "version"], capture_output=True, text=True, check=True)
        print("✅ ADB is available")
        
        # Check connected devices
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header line
        connected_devices = [line.split('\t')[0] for line in lines if line.strip() and 'device' in line]
        
        if connected_devices:
            print(f"✅ Found {len(connected_devices)} connected Android device(s):")
            for device in connected_devices:
                print(f"   📱 {device}")
            return True
        else:
            print("❌ No Android devices found via ADB")
            print("💡 Make sure USB debugging is enabled and device is connected")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ ADB not found or not working")
        print("💡 Make sure Android SDK Platform Tools are installed and in PATH")
        return False
    except FileNotFoundError:
        print("❌ ADB command not found")
        print("💡 Install Android SDK Platform Tools and add to PATH")
        return False

def turn_off_android_camera():
    """
    Turn off Android camera by force-stopping camera apps and blocking camera access.
    """
    print("🔴 Turning OFF Android camera...")
    
    if not check_adb_connection():
        return
    
    try:
        # List of common camera package names
        camera_packages = [
            "com.android.camera",
            "com.android.camera2", 
            "com.google.android.GoogleCamera",
            "com.samsung.android.camera",
            "com.huawei.camera",
            "com.oneplus.camera",
            "com.xiaomi.camera",
            "org.codeaurora.snapcam"
        ]
        
        # Force stop camera applications
        for package in camera_packages:
            try:
                subprocess.run(["adb", "shell", "am", "force-stop", package], 
                             capture_output=True, text=True, check=False)
                print(f"🛑 Stopped camera package: {package}")
            except Exception:
                continue
        
        # Disable camera permission for common apps (reversible)
        print("🔒 Disabling camera permissions...")
        common_apps = [
            "com.android.camera",
            "com.google.android.GoogleCamera", 
            "com.whatsapp",
            "com.instagram.android",
            "com.snapchat.android",
            "com.facebook.katana",
            "com.skype.raider",
            "us.zoom.videomeetings"
        ]
        
        for app in common_apps:
            try:
                # Revoke camera permission
                subprocess.run(["adb", "shell", "pm", "revoke", app, "android.permission.CAMERA"], 
                             capture_output=True, text=True, check=False)
                print(f"🚫 Revoked camera permission for: {app}")
            except Exception:
                continue
        
        # Turn off flashlight if it's on
        try:
            subprocess.run(["adb", "shell", "settings", "put", "system", "flashlight_enabled", "0"],
                         capture_output=True, text=True, check=False)
            print("🔦 Turned off flashlight")
        except Exception:
            pass
        
        # Create a black screen overlay (if possible)
        try:
            # Send input to turn screen off temporarily
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_POWER"], 
                         capture_output=True, text=True, check=False)
            time.sleep(0.5)
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_POWER"], 
                         capture_output=True, text=True, check=False)
            print("📱 Screen toggled to refresh")
        except Exception:
            pass
            
        print("✅ Android camera turned OFF successfully!")
        print("💡 Camera apps stopped and permissions revoked")
        
    except Exception as e:
        print(f"❌ Error turning off camera: {e}")

def turn_on_android_camera():
    """
    Turn on Android camera by restoring camera permissions and launching camera app.
    """
    print("🟢 Turning ON Android camera...")
    
    if not check_adb_connection():
        return
    
    try:
        # Restore camera permissions for common apps
        print("🔓 Restoring camera permissions...")
        common_apps = [
            "com.android.camera",
            "com.google.android.GoogleCamera",
            "com.whatsapp", 
            "com.instagram.android",
            "com.snapchat.android",
            "com.facebook.katana",
            "com.skype.raider",
            "us.zoom.videomeetings"
        ]
        
        for app in common_apps:
            try:
                # Grant camera permission
                subprocess.run(["adb", "shell", "pm", "grant", app, "android.permission.CAMERA"],
                             capture_output=True, text=True, check=False)
                print(f"✅ Granted camera permission for: {app}")
            except Exception:
                continue
        
        # Try to launch default camera app
        try:
            # Try common camera intents
            camera_intents = [
                "android.media.action.IMAGE_CAPTURE",
                "android.intent.action.MAIN"
            ]
            
            # Launch camera app
            subprocess.run(["adb", "shell", "am", "start", "-a", "android.media.action.IMAGE_CAPTURE"],
                         capture_output=True, text=True, check=False)
            print("📸 Launched camera app")
            
        except Exception:
            print("⚠️ Could not launch camera app automatically")
        
        print("✅ Android camera turned ON successfully!")
        print("💡 Camera permissions restored - try opening camera app manually if needed")
        
    except Exception as e:
        print(f"❌ Error turning on camera: {e}")

def create_black_screen_android():
    """
    Create a black screen effect on Android by setting brightness to minimum and launching black screen.
    """
    print("⚫ Creating black screen effect on Android...")
    
    if not check_adb_connection():
        return
    
    try:
        # Set screen brightness to minimum
        subprocess.run(["adb", "shell", "settings", "put", "system", "screen_brightness", "0"],
                     capture_output=True, text=True, check=False)
        print("🔅 Set brightness to minimum")
        
        # Create a simple black screen by opening a black webpage
        black_screen_url = "data:text/html,<html><body style='background-color:black;margin:0;padding:0;'></body></html>"
        subprocess.run(["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", black_screen_url],
                     capture_output=True, text=True, check=False)
        print("⚫ Opened black screen")
        
        # Turn off camera as well
        turn_off_android_camera()
        
        print("✅ Black screen effect activated!")
        
    except Exception as e:
        print(f"❌ Error creating black screen: {e}")

def restore_android_screen():
    """
    Restore normal Android screen settings.
    """
    print("🔆 Restoring normal Android screen...")
    
    if not check_adb_connection():
        return
    
    try:
        # Restore screen brightness to auto or medium level
        subprocess.run(["adb", "shell", "settings", "put", "system", "screen_brightness_mode", "1"],
                     capture_output=True, text=True, check=False)
        print("🔆 Restored automatic brightness")
        
        # Go to home screen
        subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_HOME"],
                     capture_output=True, text=True, check=False)
        print("🏠 Returned to home screen")
        
        # Turn camera back on
        turn_on_android_camera()
        
        print("✅ Android screen restored!")
        
    except Exception as e:
        print(f"❌ Error restoring screen: {e}")

def main():
    # Install required packages before running the main program
    install_required_packages()
    
    print("Hotkeys:")
    print("    F2: Kill (close) Iriun Webcam process")
    print("    F3: Restart Iriun Webcam")
    print("    F12: Reset screenshots and registry (deletes JPG files and empties registry.json)")
    print("    F5: Turn OFF Android camera (via USB debugging)")
    print("    F6: Turn ON Android camera (via USB debugging)")
    print("    F7: Create black screen on Android + turn off camera")
    print("    F8: Restore normal Android screen + turn on camera")
    print("    F9: Check ADB connection and Android devices")
    print("    ESC: Exit the program")
    
    # Bind hotkeys
    keyboard.add_hotkey('F2', kill_iriun_webcam)
    keyboard.add_hotkey('F3', start_iriun_webcam)
    keyboard.add_hotkey('F12', reset_screenshots)
    keyboard.add_hotkey('F5', turn_off_android_camera) 
    keyboard.add_hotkey('F6', turn_on_android_camera)
    keyboard.add_hotkey('F7', create_black_screen_android)
    keyboard.add_hotkey('F8', restore_android_screen)
    keyboard.add_hotkey('F9', check_adb_connection)
    
    # Wait for the user to press the ESC key to exit the program
    keyboard.wait('esc')
    print("Exiting the script.")

if __name__ == '__main__':
    main()
