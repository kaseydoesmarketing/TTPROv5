#!/usr/bin/env python3
"""
Pre-commit hook to validate SQLite compatibility
Add this to .git/hooks/pre-commit to run automatically
"""

import subprocess
import sys
from pathlib import Path

def run_sqlite_check():
    """Run the SQLite compatibility check"""
    script_path = Path(__file__).parent / "migrations" / "sqlite_compatibility_check.py"
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("🚫 Pre-commit hook failed:")
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            print(result.stdout)
            return True
            
    except Exception as e:
        print(f"❌ Error running SQLite compatibility check: {e}")
        return False

def check_models_file():
    """Check if models.py has been modified"""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        
        modified_files = result.stdout.split('\n')
        return any('models.py' in file for file in modified_files)
        
    except Exception:
        return True  # If we can't check, assume models were modified

def main():
    """Main pre-commit hook function"""
    if check_models_file():
        print("🔍 Database models modified, checking SQLite compatibility...")
        if not run_sqlite_check():
            sys.exit(1)
    
    print("✅ Pre-commit checks passed")

if __name__ == "__main__":
    main()