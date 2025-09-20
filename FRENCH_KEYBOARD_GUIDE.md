# 🇫🇷 French Keyboard Quiz Blink System

## Overview
This system allows you to get visual notifications (Caps Lock LED blinks) for quiz answers by pressing French keyboard keys and typing question numbers **from anywhere on your computer** - you don't need to stay in the console window!

## 🎯 How It Works

### Step 1: Start the System
```bash
python screenshot.py
```

### Step 2: Trigger Quiz Mode
Press any of these **French keyboard trigger keys**:
- `'` (apostrophe key - normally key 4)
- `&` (ampersand - normally key 1)  
- `é` (e with accent - normally key 2)
- `"` (quote - normally key 3)
- `$` (dollar sign - Shift + key 4)

### Step 3: Enter Question Number **Globally**
After pressing a trigger key, you can:
- **Switch to any application** (browser, notepad, etc.)
- **Type the question number** (1-20)
- The system will capture your keystrokes globally!

### Step 4: Confirm Your Input
- Press `Enter` to confirm
- Or wait for auto-submission (2 digits or single digit 1-9)
- Press `Escape` to cancel
- Press `Backspace` to delete last digit

### Step 5: Watch the Blink Pattern
Your Caps Lock LED will blink according to the answer:
- **A** = 1 blink
- **B** = 2 blinks  
- **C** = 3 blinks
- **D** = 4 blinks
- **E** = 5 blinks

## 📊 Quiz Data Sources
The system will automatically try:
1. **Local file**: `quiz_answers.json` (fastest)
2. **GitHub repository**: Latest data from your repo (fallback)

## 🛠️ Current Quiz Data
Based on your `quiz_answers.json`:
- **Question 1**: Answer A = 1 blink
- **Question 3**: Answer C = 3 blinks

## ⚡ Quick Example Workflow
1. You're browsing in Chrome
2. Press `é` key (trigger)
3. Stay in Chrome, type `3`
4. Press Enter
5. Caps Lock blinks 3 times (Answer C)
6. Done! 

## 🔧 Features
- ✅ Works **globally** - no need to return to console
- ✅ **French keyboard** support with multiple trigger keys
- ✅ **Auto-timeout** (10 seconds) to prevent stuck mode
- ✅ **Visual feedback** in console
- ✅ **Error handling** for invalid questions
- ✅ **Local + GitHub** data sources

## 🚨 Troubleshooting
- **No blink?** Check if Caps Lock LED is working normally
- **Wrong answer?** Verify your `quiz_answers.json` file
- **No response?** Make sure Python is running as administrator
- **Stuck in input mode?** Press `Escape` to cancel

## 🎮 All Available Hotkeys in screenshot.py
- `Tab` or `²`: Take screenshot
- `'` `&` `é` `"` `$`: Quiz blink mode
- `F1`: Test microphone
- `F2`: Kill Iriun Webcam
- `F3`: Start Iriun Webcam  
- `F4`: Toggle text recording
- `F5`: Mute microphone
- `F6`: Unmute microphone
- `F12`: Reset system
- `Esc`: Exit program
