# GitHub Quiz Integration Setup

## Overview
This system allows you to save quiz answers directly to your GitHub repository from any web browser without needing any server or authentication setup beyond a GitHub token.

## How it works
- **Web-based**: Works directly in the browser using GitHub's REST API
- **No server required**: All operations happen client-side
- **Cross-platform**: Works on any device with a web browser
- **Automatic commits**: Each answer is automatically committed and pushed to your GitHub repository

## Setup Instructions

### Step 1: Create a GitHub Personal Access Token
1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Click "Generate new token"
3. Give it a name (e.g., "Quiz Answers Token")
4. Select the `repo` scope (full repository access)
5. Click "Generate token"
6. **IMPORTANT**: Copy the token immediately (you won't see it again)

### Step 2: Configure the Web Interface
1. Open `index.html` in any web browser
2. The GitHub setup section will appear automatically
3. Paste your token in the input field
4. Click "Save Token"
5. The system will validate your token and show the quiz interface

### Step 3: Use the Quiz System
- Select or type question numbers (1-20)
- Choose answers (A, B, C, D, E)
- Click "Submit Answer" → automatically saves to GitHub
- All operations show loading states and success/error messages
- The `quiz_answers.json` file is automatically created/updated in your repository

## File Structure
```
quiz_answers.json
{
  "quiz_session": {
    "created_at": "2025-09-14T12:00:00.000Z",
    "last_updated": "2025-09-14T12:00:00.000Z", 
    "total_questions": 20,
    "answered_questions": 3
  },
  "answers": {
    "1": {
      "answer": "A",
      "answered_at": "2025-09-14T12:05:00.000Z",
      "date": "2025-09-14",
      "time": "12:05:00"
    }
  }
}
```

## Features
- ✅ **Direct GitHub Integration**: No intermediate servers
- ✅ **Real-time Commits**: Each answer creates a commit
- ✅ **Cross-device Sync**: Works from any browser/device
- ✅ **Offline Fallback**: Saves locally if GitHub is unavailable
- ✅ **Visual Feedback**: Loading states and success messages
- ✅ **Error Handling**: Graceful fallbacks and error messages
- ✅ **Token Security**: Token stored locally in browser storage

## Security Notes
- Your GitHub token is stored locally in your browser's localStorage
- The token is only used to make API calls to your own repository
- No data is sent to any third-party servers
- Use tokens with minimal required permissions (just `repo` scope)

## Troubleshooting
- **Token validation fails**: Ensure your token has `repo` permissions and access to the repository
- **Repository not found**: Check that the repository name and owner are correct in the code
- **Network errors**: The system will fall back to localStorage and show appropriate messages

## Repository
All quiz answers are saved to: `https://github.com/alemxral/screenshot/blob/main/quiz_answers.json`
