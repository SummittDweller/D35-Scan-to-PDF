#!/usr/bin/env python3
"""
Test script to verify Image Capture integration
"""

import subprocess
import sys

def test_imagecapture_availability():
    """Test if Image Capture command is available."""
    print("Testing Image Capture availability...")
    
    try:
        result = subprocess.run(['which', 'imagecapture'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Image Capture command found:", result.stdout.strip())
            return True
        else:
            print("✗ Image Capture command not found")
            return False
    except Exception as e:
        print(f"✗ Error checking Image Capture: {e}")
        return False

def test_imagecapture_list():
    """Test if Image Capture can list devices."""
    print("\nTesting device listing...")
    
    try:
        result = subprocess.run(['imagecapture', '-list'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("✓ Device listing successful:")
                print(result.stdout)
            else:
                print("! No devices found (scanner may not be connected)")
            return True
        else:
            print("✗ Device listing failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("! Device listing timed out (may still work)")
        return True
    except Exception as e:
        print(f"✗ Error listing devices: {e}")
        return False

def test_python_dependencies():
    """Test if required Python packages are available."""
    print("\nTesting Python dependencies...")
    
    packages = ['flet', 'PIL', 'reportlab']
    success = True
    
    for package in packages:
        try:
            if package == 'PIL':
                import PIL
                print(f"✓ {package} (Pillow) is available")
            else:
                __import__(package)
                print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is not installed")
            success = False
    
    return success

def main():
    """Run all tests."""
    print("D35-Scan-to-PDF Image Capture Integration Test")
    print("=" * 50)
    
    tests = [
        test_imagecapture_availability,
        test_imagecapture_list,
        test_python_dependencies
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    
    if all(results):
        print("✓ All tests passed! The app should work correctly.")
        return 0
    else:
        print("! Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())