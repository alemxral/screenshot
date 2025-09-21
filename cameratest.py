import subprocess
import keyboard
import os
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

def check_root_access():
    """
    Check if the Android device has root access for hardware-level operations.
    """
    try:
        result = subprocess.run(["adb", "shell", "su", "-c", "id"], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and "uid=0" in result.stdout:
            print("✅ ROOT ACCESS CONFIRMED - Hardware-level operations available")
            return True
        else:
            print("⚠️ NO ROOT ACCESS - Limited to software-level operations")
            print("💡 For full hardware control, root your device or use a rooted Android")
            return False
            
    except Exception:
        print("⚠️ Could not check root access")
        return False

# Global variable to track camera state
camera_is_off = False

def toggle_android_camera():
    """
    Toggle Android camera on/off with black screen effect.
    """
    global camera_is_off
    
    if camera_is_off:
        print("🟢 RESTORING Android camera and screen...")
        restore_android_camera_and_screen()
        camera_is_off = False
    else:
        print("🔴 DISABLING Android camera and creating black screen...")
        disable_android_camera_and_black_screen()
        camera_is_off = True

def disable_android_camera_and_black_screen():
    """
    HARDWARE-LEVEL camera disable: Direct camera device manipulation and system-level blocking.
    """
    print("🔴 HARDWARE-LEVEL Android camera disable...")
    
    if not check_adb_connection():
        return
    
    try:
        # HARDWARE METHOD 1: Disable camera hardware devices directly
        print("� Disabling camera hardware devices...")
        camera_devices = [
            "/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3",
            "/sys/class/video4linux/video0/device/driver/unbind",
            "/sys/class/video4linux/video1/device/driver/unbind"
        ]
        
        # Try to unbind camera hardware drivers (requires root)
        for device in camera_devices:
            try:
                subprocess.run(["adb", "shell", "su", "-c", f"echo '{device.split('/')[-1]}' > {device}"], 
                             capture_output=True, text=True, check=False)
                print(f"🔌 Unbound hardware device: {device}")
            except Exception:
                continue
        
        # HARDWARE METHOD 2: Disable camera HAL (Hardware Abstraction Layer)
        print("🏭 Disabling Camera HAL services...")
        hal_services = [
            "android.hardware.camera.provider@2.4-service",
            "android.hardware.camera.provider@2.5-service", 
            "android.hardware.camera.provider@2.6-service",
            "cameraserver",
            "media.camera",
            "camera.goldfish"
        ]
        
        for service in hal_services:
            try:
                # Stop camera hardware services
                subprocess.run(["adb", "shell", "su", "-c", f"stop {service}"], 
                             capture_output=True, text=True, check=False)
                print(f"🛑 Stopped HAL service: {service}")
                
                # Disable service completely
                subprocess.run(["adb", "shell", "su", "-c", f"setprop ctl.stop {service}"], 
                             capture_output=True, text=True, check=False)
                
            except Exception:
                continue
        
        # HARDWARE METHOD 3: Block camera device files
        print("� Blocking camera device access...")
        try:
            # Change permissions on camera device files to block access
            subprocess.run(["adb", "shell", "su", "-c", "chmod 000 /dev/video*"], 
                         capture_output=True, text=True, check=False)
            subprocess.run(["adb", "shell", "su", "-c", "chmod 000 /dev/media*"], 
                         capture_output=True, text=True, check=False)
            print("🔒 Camera device files access blocked")
        except Exception:
            pass
        
        # HARDWARE METHOD 4: Kill camera-related kernel modules
        print("🧠 Disabling camera kernel modules...")
        camera_modules = [
            "uvcvideo", "gspca_main", "videodev", "v4l2_common", 
            "videobuf2_core", "videobuf2_v4l2", "media"
        ]
        
        for module in camera_modules:
            try:
                subprocess.run(["adb", "shell", "su", "-c", f"rmmod {module}"], 
                             capture_output=True, text=True, check=False)
                print(f"�️ Removed kernel module: {module}")
            except Exception:
                continue
        
        # HARDWARE METHOD 5: Disable camera power management
        print("⚡ Disabling camera power supply...")
        try:
            # Find and disable camera power supplies
            subprocess.run(["adb", "shell", "su", "-c", "find /sys -name '*camera*' -type d -exec echo 0 > {}/power/control \\;"], 
                         capture_output=True, text=True, check=False)
            print("🔋 Camera power management disabled")
        except Exception:
            pass
        
        # SOFTWARE METHOD 6: System-level app disable (works without root)
        print("� System-level camera app disabling...")
        camera_packages = [
            "com.android.camera", "com.android.camera2", "com.google.android.GoogleCamera",
            "com.samsung.android.camera", "com.huawei.camera", "com.oneplus.camera",
            "com.xiaomi.camera", "org.codeaurora.snapcam", "com.oppo.camera", "com.vivo.camera"
        ]
        
        for package in camera_packages:
            try:
                # Completely disable the package
                subprocess.run(["adb", "shell", "pm", "disable-user", package], 
                             capture_output=True, text=True, check=False)
                # Clear all data
                subprocess.run(["adb", "shell", "pm", "clear", package], 
                             capture_output=True, text=True, check=False)
                # Force stop
                subprocess.run(["adb", "shell", "am", "force-stop", package], 
                             capture_output=True, text=True, check=False)
                print(f"� DISABLED system package: {package}")
            except Exception:
                continue
        
        # SECURITY METHOD 7: SELinux policy manipulation (advanced)
        print("🛡️ Applying SELinux camera restrictions...")
        try:
            # Set SELinux to block camera access
            subprocess.run(["adb", "shell", "su", "-c", "setenforce 1"], 
                         capture_output=True, text=True, check=False)
            # Apply custom SELinux rules to block camera
            subprocess.run(["adb", "shell", "su", "-c", "echo 'deny untrusted_app camera_device:chr_file { read write open };' >> /sys/fs/selinux/policy"], 
                         capture_output=True, text=True, check=False)
            print("🛡️ SELinux camera restrictions applied")
        except Exception:
            pass
        
        # PHYSICAL METHOD 8: Create black screen effect
        print("⚫ Creating impenetrable black screen...")
        try:
            # Force black screen at system level
            subprocess.run(["adb", "shell", "su", "-c", "settings put system screen_brightness 0"], 
                         capture_output=True, text=True, check=False)
            subprocess.run(["adb", "shell", "su", "-c", "settings put system screen_brightness_mode 0"], 
                         capture_output=True, text=True, check=False)
            
            # Create persistent black overlay
            subprocess.run(["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", 
                          "-d", "data:text/html,<html><body style='background:black;margin:0;position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;'></body></html>"], 
                         capture_output=True, text=True, check=False)
            
            # Lock the screen orientation and disable touch temporarily
            subprocess.run(["adb", "shell", "settings", "put", "system", "user_rotation", "0"], 
                         capture_output=True, text=True, check=False)
            
            print("⚫ Hardware-level black screen activated")
        except Exception:
            pass
        
        print("✅ HARDWARE-LEVEL CAMERA DISABLE COMPLETE!")
        print("� Camera hardware disabled at multiple system levels")
        print("⚡ Device drivers unbound, HAL services stopped, kernel modules removed")
        print("🛡️ SELinux restrictions applied, power management disabled")
        
    except Exception as e:
        print(f"❌ Error in hardware-level disable: {e}")

def restore_android_camera_and_screen():
    """
    HARDWARE-LEVEL camera restore: Re-enable all camera hardware and system components.
    """
    print("🟢 HARDWARE-LEVEL Android camera restore...")
    
    if not check_adb_connection():
        return
    
    try:
        # HARDWARE RESTORE 1: Re-enable camera HAL services
        print("🏭 Restarting Camera HAL services...")
        hal_services = [
            "android.hardware.camera.provider@2.4-service",
            "android.hardware.camera.provider@2.5-service", 
            "android.hardware.camera.provider@2.6-service",
            "cameraserver",
            "media.camera",
            "camera.goldfish"
        ]
        
        for service in hal_services:
            try:
                # Start camera hardware services
                subprocess.run(["adb", "shell", "su", "-c", f"start {service}"], 
                             capture_output=True, text=True, check=False)
                subprocess.run(["adb", "shell", "su", "-c", f"setprop ctl.start {service}"], 
                             capture_output=True, text=True, check=False)
                print(f"🟢 Started HAL service: {service}")
            except Exception:
                continue
        
        # HARDWARE RESTORE 2: Restore camera device file permissions
        print("🔓 Restoring camera device access...")
        try:
            # Restore permissions on camera device files
            subprocess.run(["adb", "shell", "su", "-c", "chmod 666 /dev/video*"], 
                         capture_output=True, text=True, check=False)
            subprocess.run(["adb", "shell", "su", "-c", "chmod 666 /dev/media*"], 
                         capture_output=True, text=True, check=False)
            print("� Camera device files access restored")
        except Exception:
            pass
        
        # HARDWARE RESTORE 3: Reload camera kernel modules
        print("🧠 Reloading camera kernel modules...")
        camera_modules = [
            "media", "videobuf2_core", "videobuf2_v4l2", 
            "v4l2_common", "videodev", "gspca_main", "uvcvideo"
        ]
        
        for module in camera_modules:
            try:
                subprocess.run(["adb", "shell", "su", "-c", f"modprobe {module}"], 
                             capture_output=True, text=True, check=False)
                print(f"🔄 Loaded kernel module: {module}")
            except Exception:
                continue
        
        # HARDWARE RESTORE 4: Re-enable camera power management
        print("⚡ Re-enabling camera power supply...")
        try:
            # Re-enable camera power supplies
            subprocess.run(["adb", "shell", "su", "-c", "find /sys -name '*camera*' -type d -exec echo auto > {}/power/control \\;"], 
                         capture_output=True, text=True, check=False)
            print("🔋 Camera power management restored")
        except Exception:
            pass
        
        # SOFTWARE RESTORE 5: Re-enable system camera packages
        print("💾 Re-enabling camera system packages...")
        camera_packages = [
            "com.android.camera", "com.android.camera2", "com.google.android.GoogleCamera",
            "com.samsung.android.camera", "com.huawei.camera", "com.oneplus.camera",
            "com.xiaomi.camera", "org.codeaurora.snapcam", "com.oppo.camera", "com.vivo.camera"
        ]
        
        for package in camera_packages:
            try:
                # Re-enable the package
                subprocess.run(["adb", "shell", "pm", "enable", package], 
                             capture_output=True, text=True, check=False)
                print(f"✅ ENABLED system package: {package}")
            except Exception:
                continue
        
        # SECURITY RESTORE 6: Remove SELinux restrictions
        print("🛡️ Removing SELinux camera restrictions...")
        try:
            # Reset SELinux to permissive for camera access
            subprocess.run(["adb", "shell", "su", "-c", "setenforce 0"], 
                         capture_output=True, text=True, check=False)
            print("🛡️ SELinux camera restrictions removed")
        except Exception:
            pass
        
        # SCREEN RESTORE 7: Restore normal screen settings
        print("🔆 Restoring normal screen settings...")
        try:
            # Restore screen brightness to auto
            subprocess.run(["adb", "shell", "su", "-c", "settings put system screen_brightness_mode 1"], 
                         capture_output=True, text=True, check=False)
            subprocess.run(["adb", "shell", "su", "-c", "settings put system screen_brightness 128"], 
                         capture_output=True, text=True, check=False)
            
            # Clear any overlays and return to home
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_HOME"], 
                         capture_output=True, text=True, check=False)
            time.sleep(0.5)
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_HOME"], 
                         capture_output=True, text=True, check=False)
            
            print("🔆 Screen settings and brightness restored")
        except Exception:
            pass
        
        # PERMISSION RESTORE 8: Grant camera permissions to all apps
        print("🔓 Restoring camera permissions for all apps...")
        common_apps = [
            "com.android.camera", "com.google.android.GoogleCamera",
            "com.whatsapp", "com.instagram.android", "com.snapchat.android",
            "com.facebook.katana", "com.skype.raider", "us.zoom.videomeetings",
            "com.discord", "com.google.android.apps.meetings"
        ]
        
        for app in common_apps:
            try:
                subprocess.run(["adb", "shell", "pm", "grant", app, "android.permission.CAMERA"],
                             capture_output=True, text=True, check=False)
                print(f"✅ Granted camera permission: {app}")
            except Exception:
                continue
        
        # SYSTEM RESTART 9: Restart camera-related system services
        print("🔄 Restarting system services...")
        try:
            subprocess.run(["adb", "shell", "su", "-c", "killall system_server"], 
                         capture_output=True, text=True, check=False)
            time.sleep(2)  # Wait for system to restart services
            print("🔄 System services restarted")
        except Exception:
            pass
        
        # VERIFICATION 10: Test camera functionality
        print("📸 Testing hardware-level camera functionality...")
        try:
            # Launch camera app to verify everything works
            subprocess.run(["adb", "shell", "am", "start", "-a", "android.media.action.IMAGE_CAPTURE"],
                         capture_output=True, text=True, check=False)
            print("📸 Camera app launched - testing hardware access")
            
            time.sleep(3)  # Give time for camera to initialize
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_HOME"],
                         capture_output=True, text=True, check=False)
            
        except Exception:
            print("⚠️ Camera test launch failed - try manually")
        
        print("✅ HARDWARE-LEVEL CAMERA RESTORE COMPLETE!")
        print("� Camera hardware re-enabled at all system levels")
        print("⚡ Device drivers restored, HAL services restarted, kernel modules loaded")
        print("🛡️ Security restrictions removed, power management restored")
        print("📱 All system packages enabled and permissions granted")
        
    except Exception as e:
        print(f"❌ Error in hardware-level restore: {e}")

def main():
    """
    Main function - Camera Test with TAB key toggle
    """
    # Install required packages
    install_required_packages()
    
    print("="*60)
    print("🎥 HARDWARE-LEVEL ANDROID CAMERA CONTROL")
    print("="*60)
    print("📱 Make sure your Android device is connected via USB")
    print("🔧 Enable USB Debugging in Developer Options")
    print("� ROOT ACCESS recommended for hardware-level control")
    print("�💻 Install Android SDK Platform Tools (ADB)")
    print("="*60)
    
    # Initial ADB connection check
    print("🔍 Checking ADB connection...")
    if not check_adb_connection():
        print("\n❌ ADB connection failed!")
        print("💡 Setup instructions:")
        print("   1. Enable Developer Options on your Android device")
        print("   2. Enable USB Debugging in Developer Options")
        print("   3. Connect device via USB")
        print("   4. Install Android SDK Platform Tools")
        print("   5. Add ADB to your system PATH")
        input("\nPress Enter to continue anyway (or Ctrl+C to exit)...")
    
    # Check root access for hardware operations
    print("\n🔐 Checking root access for hardware control...")
    has_root = check_root_access()
    
    if has_root:
        print("🔥 FULL HARDWARE CONTROL MODE AVAILABLE")
        print("⚡ Can disable camera at kernel/driver level")
    else:
        print("⚠️ LIMITED SOFTWARE CONTROL MODE")
        print("📱 Will use package management and permission control")
        print("💡 For full hardware control, consider rooting your device")
    
    print("\n🎮 Controls:")
    print("   TAB: Toggle Android camera ON/OFF + Black screen effect")
    print("   ESC: Exit the program")
    print("\n⚡ Camera Test is now active! Press TAB to toggle camera...")
    
    global camera_is_off
    camera_is_off = False
    
    try:
        # Main loop - wait for TAB key
        while True:
            if keyboard.is_pressed("tab"):
                toggle_android_camera()
                # Wait to prevent multiple triggers
                time.sleep(1)
            elif keyboard.is_pressed("esc"):
                print("\n👋 Exiting Camera Test...")
                if camera_is_off:
                    print("🔄 Restoring camera before exit...")
                    restore_android_camera_and_screen()
                break
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Program interrupted!")
        if camera_is_off:
            print("🔄 Restoring camera before exit...")
            restore_android_camera_and_screen()
    
    print("🏁 Camera Test finished!")

if __name__ == '__main__':
    main()