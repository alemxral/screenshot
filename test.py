import subprocess
import keyboard
import os

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

def main():
    print("Hotkeys:")
    print("    F2: Kill (close) Iriun Webcam process")
    print("    F3: Restart Iriun Webcam")
    print("    ESC: Exit the program")
    
    # Bind hotkeys for F2 (kill) and F3 (restart)
    keyboard.add_hotkey('F2', kill_iriun_webcam)
    keyboard.add_hotkey('F3', start_iriun_webcam)
    
    # Wait for the user to press the ESC key to exit the program
    keyboard.wait('esc')
    print("Exiting the script.")

if __name__ == '__main__':
    main()
