#!/usr/bin/env python3
"""
Discord Bot Setup Script
Automated setup for Discord bot dependencies
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    packages = [
        'discord.py>=2.3.0',
        'python-dotenv>=1.0.0',
        'gtts>=2.5.0',
        'aiohttp>=3.8.0',
        'psutil>=5.9.0'
    ]
    
    print("Installing Discord bot dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Discord Bot Configuration\n")
            f.write("DISCORD_TOKEN=your_discord_bot_token_here\n\n")
            f.write("# Bot Settings\n")
            f.write("BOT_PREFIX=!\n")
        print("✓ .env file created - please add your Discord bot token")
    else:
        print("✓ .env file already exists")

def main():
    """Main setup function"""
    print("Discord Bot Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("Setup failed - could not install all dependencies")
        return
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Discord bot token")
    print("2. Run: python main.py")
    print("\nFor help, see README.md")

if __name__ == "__main__":
    main()