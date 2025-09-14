import subprocess
import keyboard
import os
import json
import glob
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
        
        # Delete all JPG files in the screenshots folder
        if os.path.exists(screenshots_dir):
            jpg_files = glob.glob(os.path.join(screenshots_dir, "*.jpg"))
            for jpg_file in jpg_files:
                os.remove(jpg_file)
                print(f"Deleted: {os.path.basename(jpg_file)}")
            
            if jpg_files:
                print(f"Deleted {len(jpg_files)} JPG files from screenshots folder.")
            else:
                print("No JPG files found in screenshots folder.")
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

def main():
    # Install required packages before running the main program
    install_required_packages()
    
    print("Hotkeys:")
    print("    F2: Kill (close) Iriun Webcam process")
    print("    F3: Restart Iriun Webcam")
    print("    F12: Reset screenshots and registry (deletes JPG files and empties registry.json)")
    print("    ESC: Exit the program")
    
    # Bind hotkeys
    keyboard.add_hotkey('F2', kill_iriun_webcam)
    keyboard.add_hotkey('F3', start_iriun_webcam)
    keyboard.add_hotkey('F12', reset_screenshots)
    
    # Wait for the user to press the ESC key to exit the program
    keyboard.wait('esc')
    print("Exiting the script.")

if __name__ == '__main__':
    main()
