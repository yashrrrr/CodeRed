#!/usr/bin/env python
"""
Setup Python Scripts in PATH for Windows
Adds Python Scripts directories to system PATH permanently
"""

import os
import sys
import subprocess
from pathlib import Path

def add_to_path_windows():
    """Add Python Scripts to Windows PATH"""

    # Get Python Scripts directories
    python_dir = Path(sys.executable).parent
    scripts_dirs = [
        str(python_dir / "Scripts"),  # System Python Scripts
        str(Path.home() / "AppData" / "Roaming" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts")  # User Scripts
    ]

    print("=" * 60)
    print("Python Scripts PATH Setup for Windows")
    print("=" * 60)
    print("\nPython Scripts directories to add to PATH:")
    for dir_path in scripts_dirs:
        if Path(dir_path).exists():
            print(f"  [OK] {dir_path}")
        else:
            print(f"  [X] {dir_path} (not found)")

    print("\n" + "=" * 60)
    print("To add these to PATH permanently:")
    print("=" * 60)

    print("\n### Option 1: Using Windows Settings (Recommended)")
    print("1. Press Windows + X, select 'System'")
    print("2. Click 'Advanced system settings'")
    print("3. Click 'Environment Variables'")
    print("4. Under 'System variables', find and select 'Path', click 'Edit'")
    print("5. Click 'New' and add each of these paths:")
    for dir_path in scripts_dirs:
        if Path(dir_path).exists():
            print(f"   {dir_path}")
    print("6. Click 'OK' on all dialogs")
    print("7. Restart your terminal/command prompt")

    print("\n### Option 2: Using PowerShell (Run as Administrator)")
    print("Copy and run this command in PowerShell as Administrator:\n")

    # Create PowerShell command
    ps_command = "[Environment]::SetEnvironmentVariable('Path', "
    ps_command += f"'{';'.join(scripts_dirs)};' + "
    ps_command += "[Environment]::GetEnvironmentVariable('Path', 'Machine'), 'Machine')"

    print(f"  {ps_command}")

    print("\n### Option 3: Using Command Prompt (Run as Administrator)")
    print("Copy and run this command in Command Prompt as Administrator:\n")

    # Create setx command
    cmd_command = f'setx /M PATH "%PATH%;{";".join(scripts_dirs)}"'
    print(f"  {cmd_command}")

    print("\n" + "=" * 60)
    print("After adding to PATH, you can use commands directly:")
    print("=" * 60)
    print("  streamlit run dashboard/app.py")
    print("  uvicorn backend.app:app")
    print("\nInstead of:")
    print("  python -m streamlit run dashboard/app.py")
    print("  python -m uvicorn backend.app:app")

    # Create a batch file for easy setup
    batch_content = f"""@echo off
echo Adding Python Scripts to PATH...
setx /M PATH "%PATH%;{';'.join(scripts_dirs)}"
echo Done! Please restart your terminal.
pause
"""

    batch_file = Path("add_to_path_admin.bat")
    batch_file.write_text(batch_content)
    print(f"\n[OK] Created 'add_to_path_admin.bat' - Run as Administrator to add to PATH")

def check_in_path():
    """Check if Python Scripts are already in PATH"""
    import shutil

    commands = ["streamlit", "uvicorn", "pip"]
    print("\nChecking availability of commands:")
    print("-" * 40)

    all_available = True
    for cmd in commands:
        path = shutil.which(cmd)
        if path:
            print(f"[OK] {cmd:10} -> {path}")
        else:
            print(f"[X] {cmd:10} -> Not found in PATH")
            all_available = False

    return all_available

def main():
    """Main execution"""
    # Check current status
    if check_in_path():
        print("\n[OK] All commands are already available in PATH!")
        print("You can use streamlit and uvicorn directly.")
    else:
        print("\nWarning: Some commands are not in PATH.")
        add_to_path_windows()

if __name__ == "__main__":
    main()