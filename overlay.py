"""
Overlay helper: show a fullscreen topmost image of the current screen for a few seconds.
This uses tkinter and Pillow. Designed to be lightweight and to work from a frozen exe when bundled.
"""
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui
import threading
import time


def _show(duration_seconds=2):
    try:
        img = pyautogui.screenshot()
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.config(cursor='none')
        # Convert screenshot to PhotoImage
        pil = img.convert('RGB')
        screen_w, screen_h = pil.size
        tk_img = ImageTk.PhotoImage(pil)
        lbl = tk.Label(root, image=tk_img)
        lbl.place(x=0, y=0, relwidth=1, relheight=1)
        # Close after duration_seconds
        def closer():
            time.sleep(duration_seconds)
            try:
                root.destroy()
            except Exception:
                pass
        t = threading.Thread(target=closer, daemon=True)
        t.start()
        root.mainloop()
    except Exception as e:
        print(f"Overlay show failed: {e}")


def show_overlay(duration_seconds=2):
    # Run the overlay on the main thread briefly; this will block until closed
    _show(duration_seconds=duration_seconds)
