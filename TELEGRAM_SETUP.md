# 📱 Telegram Vibration Bot Setup Guide

## 🚀 Quick Start

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Telegram Bot
1. Open Telegram and message **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot
4. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Setup Your Bot
```bash
python telegram_bot.py
```
- Paste your bot token when prompted
- Send any message to your new bot in Telegram
- Press Enter in the terminal
- The script will automatically get your Chat ID and save configuration

### Step 4: Test the System
```bash
python send_vibration.py 5
```
This will send a vibration notification for question 5.

## 🎯 How to Use

### Method 1: From Web Interface
1. Open your quiz application in the browser
2. Press **Shift + !** (exclamation mark key)
3. Enter the question number (1-20)
4. The command will be copied to your clipboard
5. Run the command in terminal

### Method 2: Direct Terminal Usage
```bash
python send_vibration.py <question_number>
```

Examples:
```bash
python send_vibration.py 1    # Question 1 -> Answer A = 1 vibration
python send_vibration.py 5    # Question 5 -> Answer B = 2 vibrations
python send_vibration.py 10   # Question 10 -> Answer C = 3 vibrations
```

## 📳 Vibration Patterns

| Answer | Pattern | Vibrations |
|--------|---------|------------|
| **A** | • | 1 vibration |
| **B** | •• | 2 vibrations |
| **C** | ••• | 3 vibrations |
| **D** | •••• | 4 vibrations |
| **E** | ••••• | 5 vibrations |

## 📁 Files Created

- `telegram_bot.py` - Main bot setup script
- `send_vibration.py` - Quick notification sender
- `telegram_config.json` - Your bot configuration (auto-created)

## 🛠️ Troubleshooting

### "Configuration not found"
- Run `python telegram_bot.py` first to set up your bot

### "No answer found for question X"
- Make sure the question has an answer in your GitHub quiz data
- Check that `quiz_answers.json` exists in your repository

### "Failed to send message"
- Verify your bot token is correct
- Make sure you've sent at least one message to your bot
- Check your internet connection

## 🔧 Advanced Usage

### Auto-run on key press (Windows)
You can create a batch file to make it even easier:

Create `vibrate.bat`:
```batch
@echo off
python send_vibration.py %1
pause
```

Then you can just double-click and enter the question number.

## 🔐 Security Notes

- Your bot token is stored in `telegram_config.json` - keep this file private
- The bot can only send messages to you (using your Chat ID)
- All communication is encrypted through Telegram's API

## 📞 Support

If you have issues:
1. Check that Python 3.6+ is installed
2. Verify `requests` library is installed: `pip install requests`
3. Make sure your bot token is valid
4. Ensure you've messaged your bot at least once
