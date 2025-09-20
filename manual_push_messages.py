#!/usr/bin/env python3
"""
Manual Git Push for Messages
Pushes any pending messages.json changes to GitHub
"""

import asyncio
import subprocess
import os
import json

async def manual_push_messages():
    """Manually push any pending messages.json changes"""
    print("🔄 Manual Push for Messages.json")
    print("=" * 40)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    messages_file = "messages.json"
    
    try:
        # Check if messages.json exists
        messages_path = os.path.join(project_root, messages_file)
        if not os.path.exists(messages_path):
            print("❌ messages.json not found")
            return False
        
        # Show current messages count
        with open(messages_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        print(f"📚 Found {len(messages)} messages in messages.json")
        
        if messages:
            # Show latest message
            latest = messages[-1]
            print(f"📝 Latest message: '{latest['message'][:50]}...' ({latest['timestamp']})")
        
        # Check git status
        print("\n🔍 Checking git status...")
        proc = await asyncio.create_subprocess_exec(
            "git", "status", "--porcelain", messages_file,
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        git_status = stdout.decode().strip()
        if not git_status:
            print("✅ messages.json is up to date with git")
            return True
        else:
            print(f"📝 Git status: {git_status}")
            print("🔄 Pushing changes...")
        
        # Add to git
        print("📝 Adding messages.json to git...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "add", messages_file,
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
        else:
            print(f" ❌ Error: {stderr.decode().strip()}")
            return False
        
        # Commit
        commit_message = f"Manual push: Update messages.json with {len(messages)} messages"
        print("📝 Committing changes...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", commit_message,
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
        else:
            stderr_text = stderr.decode().strip()
            if "nothing to commit" in stderr_text:
                print(" ⏭️ (Nothing to commit)")
            else:
                print(f" ❌ Error: {stderr_text}")
                return False
        
        # Push
        print("🚀 Pushing to remote repository...", end="", flush=True)
        proc = await asyncio.create_subprocess_exec(
            "git", "push",
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print(" ✅")
            print("🎉 Messages successfully pushed to GitHub!")
            return True
        else:
            print(f" ❌ Error: {stderr.decode().strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during manual push: {e}")
        return False

async def check_git_repo_status():
    """Check overall git repository status"""
    print("\n🔍 Git Repository Status Check")
    print("=" * 30)
    
    try:
        # Check if we're in a git repo
        proc = await asyncio.create_subprocess_exec(
            "git", "status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            print("✅ Git repository detected")
            
            # Show branch info
            proc = await asyncio.create_subprocess_exec(
                "git", "branch", "--show-current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                branch = stdout.decode().strip()
                print(f"🌿 Current branch: {branch}")
            
            # Check for uncommitted changes
            proc = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            changes = stdout.decode().strip()
            if changes:
                print("📝 Uncommitted changes:")
                for line in changes.split('\n'):
                    print(f"   {line}")
            else:
                print("✅ No uncommitted changes")
            
            # Check remote connection
            print("🌐 Testing remote connection...", end="", flush=True)
            proc = await asyncio.create_subprocess_exec(
                "git", "remote", "get-url", "origin",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                remote_url = stdout.decode().strip()
                print(f" ✅")
                print(f"🔗 Remote URL: {remote_url}")
            else:
                print(" ❌ No remote configured")
            
        else:
            print("❌ Not a git repository or git not available")
            print(f"Error: {stderr.decode().strip()}")
            
    except Exception as e:
        print(f"❌ Error checking git status: {e}")

async def main():
    """Main function"""
    print("🔧 Messages.json Git Push Tool")
    print("=" * 50)
    
    # Check git repository status
    await check_git_repo_status()
    
    # Manual push messages
    success = await manual_push_messages()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Operation completed successfully!")
        print("📱 Your messages should now be visible on GitHub")
    else:
        print("❌ Operation failed!")
        print("💡 Possible solutions:")
        print("   • Check your internet connection")
        print("   • Verify git credentials are set up")
        print("   • Run 'git status' to check repository state")
        print("   • Make sure you have push permissions to the repo")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
