#!/usr/bin/env python3
"""
Setup and installation check for D35 Scanner to PDF application
"""

import sys
import subprocess
import os


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required. You have {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_sane():
    """Check if SANE is installed."""
    print("\nChecking SANE installation...")
    try:
        result = subprocess.run(
            ["scanimage", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ SANE is installed: {result.stdout.strip().split()[0]}")
            return True
        else:
            print("❌ SANE is installed but not working correctly")
            return False
    except FileNotFoundError:
        print("❌ SANE (scanimage) not found")
        print("\nInstallation instructions:")
        print("  Ubuntu/Debian: sudo apt-get install sane sane-utils libsane-dev")
        print("  Fedora/RHEL:   sudo dnf install sane-backends sane-backends-drivers-scanners")
        print("  macOS:         brew install sane-backends")
        return False
    except Exception as e:
        print(f"❌ Error checking SANE: {e}")
        return False


def check_scanners():
    """Check for available scanners."""
    print("\nChecking for scanners...")
    try:
        result = subprocess.run(
            ["scanimage", "-L"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout.strip()
        if output and "device" in output.lower():
            print(f"✓ Scanner(s) found:")
            print(f"  {output}")
            return True
        else:
            print("⚠ No scanners detected")
            print("  Make sure your scanner is:")
            print("    - Connected to the computer")
            print("    - Powered on")
            print("    - Properly configured in SANE")
            return False
    except FileNotFoundError:
        print("❌ Cannot check scanners (scanimage not found)")
        return False
    except Exception as e:
        print(f"⚠ Error checking scanners: {e}")
        return False


def check_dependencies():
    """Check if Python dependencies are installed."""
    print("\nChecking Python dependencies...")
    required_packages = ['flet', 'sane', 'PIL', 'reportlab']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'sane':
                __import__('sane')
            elif package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("D35 Scanner to PDF - Setup Check")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_sane(),
        check_dependencies(),
        check_scanners(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks[:3]):  # Required checks
        print("✓ All required components are installed!")
        if not checks[3]:
            print("⚠ Note: No scanners detected, but you can still run the app")
        print("\nYou can now run the application with:")
        print("  python scanner_app.py")
        print("  or")
        print("  ./run.sh")
    else:
        print("❌ Setup incomplete. Please install missing components.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
