# Screenshot App — Keyboard Commands

This file lists all keyboard shortcuts and behaviors for `screenshot.py`.

## Quick Reference

- **Esc**
  - Take a screenshot (saved in `screenshots/`).
- **²** (key right of `1` on some layouts)
  - Alternative screenshot key.
- **Double Shift (Left/Right)**
  - Toggle text recording mode (start/stop).
  - Single Shift while recording saves message to `messages.json`.
- **Right Arrow**
  - Activate QUIZ BLINK MODE: type question number (1–20), blink Caps Lock for answer.
- **Left Arrow (during quiz input)**
  - Submit question number, blink answer (A=1, B=2, C=3, D=4, E=5).
- **Escape (during quiz input)**
  - Cancel quiz input mode.
- **Down Arrow**
  - Download latest `quiz_answers.json` from GitHub, then send unsent screenshots/messages to Telegram.
- **Up Arrow**
  - Send unsent screenshots/messages to Telegram group.
- **Delete / Supr**
  - Delete messages sent by bot in Telegram group.
- **F7**
  - Activate stealth mode: reduce mic sensitivity, play white noise.
- **F8**
  - Restore mic sensitivity, stop white noise.
- **F2**
  - Kill Iriun Webcam processes.
- **F3**
  - Restart Iriun Webcam.
- **F10**
  - Clear screenshots, registry, and messages (does not touch quiz/telegram config).
- **Double F12**
  - Exit program (blinks Caps Lock 3 times).
- **F9**
  - Scroll current page/window to top (Ctrl+Home + PageUp/Home burst).

## Quiz Input Details
- Type question number (1–20) in QUIZ BLINK MODE.
- French layout mappings supported (e.g. '&' or '1' → 1, 'é' or '2' → 2, etc).
- After entering digits, press Left Arrow to submit. Esc cancels.

## Text Recording
- Start: Double Shift.
- Save: Single Shift while recording.
- Messages saved to `messages.json`.


## Autotype Modes (Questions 15–20)
- After selecting Q15–Q20, you will see this prompt:
  - ⏱ Press SHIFT for SUPER-FAST typing, SPACE for HUMAN typing, '!' (Shift+1) for PASTE mode. Press SPACE during typing to stop. Waiting 5s...
  - **SHIFT** → SUPER-FAST typing (tight char loop).
  - **SPACE** → HUMAN typing (randomized delays).
  - **'!' (Shift+1)** → PASTE mode: shows fullscreen freeze overlay (default 1s), then pastes answer and scrolls to top.
- **SPACE** or **ESC** during typing cancels autotype.

## Overlay & Paste Mode
- Overlay is borderless, instant, and configurable (`OVERLAY_DURATION_SECONDS` in code).
- Paste mode triggers overlay, then Ctrl+V paste, then fast scroll-to-top.

## Build & Troubleshooting
- PyInstaller: use `--noconsole` and `--add-data` for all config/data files.
- Ensure `tkinter`, `Pillow`, `pyautogui`, `keyboard`, `numpy`, `sounddevice`, `requests`, `pywin32` are installed.
- White noise and mic control require `pycaw`, `comtypes`, and audio device permissions.

---
For more details, see `KEYBOARD_COMMANDS.md` or the comments in `screenshot.py`.