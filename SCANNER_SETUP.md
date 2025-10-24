# Scanner Setup Guide

This guide provides detailed instructions for setting up your Xerox D35 scanner with SANE on different operating systems.

## Table of Contents

- [Linux Setup](#linux-setup)
- [macOS Setup](#macos-setup)
- [Windows Setup](#windows-setup)
- [Troubleshooting](#troubleshooting)

## Linux Setup

### Ubuntu/Debian

1. Install SANE and required packages:
```bash
sudo apt-get update
sudo apt-get install sane sane-utils libsane-dev python3-dev
```

2. Add your user to the scanner group:
```bash
sudo usermod -a -G scanner $USER
# On some systems, also add to lp group:
sudo usermod -a -G lp $USER
```

3. Log out and log back in for group changes to take effect.

4. Connect your Xerox D35 scanner via USB.

5. Test scanner detection:
```bash
scanimage -L
```

### Fedora/RHEL/CentOS

1. Install SANE packages:
```bash
sudo dnf install sane-backends sane-backends-drivers-scanners python3-devel
```

2. Add your user to the scanner group:
```bash
sudo usermod -a -G scanner $USER
```

3. Log out and back in.

4. Test scanner detection:
```bash
scanimage -L
```

### Arch Linux

1. Install SANE:
```bash
sudo pacman -S sane
```

2. Add user to scanner group:
```bash
sudo usermod -a -G scanner $USER
```

3. Enable and start saned service (if using network scanning):
```bash
sudo systemctl enable saned.socket
sudo systemctl start saned.socket
```

## macOS Setup

1. Install Homebrew if not already installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install SANE backends:
```bash
brew install sane-backends
```

3. Connect your scanner.

4. Test scanner detection:
```bash
scanimage -L
```

### macOS Notes

- Some scanners may require additional drivers from the manufacturer
- USB permissions are usually handled automatically on macOS
- If you encounter issues, try restarting after driver installation

## Windows Setup

### Option 1: Windows Subsystem for Linux (WSL2)

WSL2 provides the best SANE compatibility on Windows:

1. Install WSL2 and Ubuntu:
```powershell
wsl --install
```

2. Inside WSL2, follow the [Ubuntu setup instructions](#ubuntudebian).

3. For USB support in WSL2, install usbipd:
   - On Windows (PowerShell as Administrator):
   ```powershell
   winget install --interactive --exact dorssel.usbipd-win
   ```

4. Attach USB scanner to WSL2:
   ```powershell
   # List USB devices (Windows PowerShell)
   usbipd list
   
   # Bind the scanner (replace X-X with your device bus ID)
   usbipd bind --busid X-X
   
   # Attach to WSL
   usbipd attach --wsl --busid X-X
   ```

5. In WSL2, verify scanner is detected:
   ```bash
   scanimage -L
   ```

### Option 2: Native Windows (Limited Support)

SANE support on native Windows is limited. Consider these alternatives:

1. **VueScan**: Commercial scanner software with excellent hardware support
   - Website: https://www.hamrick.com/

2. **WIA-based Python libraries**:
   - Install `wia-scan` or similar WIA-compatible libraries
   - Note: This would require modifying the application code

3. **Vendor Drivers**: Check if Xerox provides Windows drivers for the D35

## SANE Configuration

### Configure Scanner Backend

1. Edit the SANE configuration:
```bash
sudo nano /etc/sane.d/dll.conf
```

2. Ensure the appropriate backend is enabled. For Xerox scanners, uncomment:
```
xerox_mfp
```

3. For network scanners, also enable:
```
net
```

4. Save and exit.

### Configure Network Scanning (if applicable)

If using the scanner over the network:

1. Edit the network backend configuration:
```bash
sudo nano /etc/sane.d/net.conf
```

2. Add your scanner's IP address or hostname:
```
scanner.local
# or
192.168.1.100
```

3. Save and restart SANE.

## Troubleshooting

### Scanner Not Detected

**Check USB Connection:**
```bash
lsusb | grep -i xerox
```

**Check SANE Devices:**
```bash
scanimage -L
```

**Check Permissions:**
```bash
ls -l /dev/bus/usb/*/*
```

**Force Refresh:**
```bash
sudo sane-find-scanner
```

### Permission Denied Errors

**Verify Group Membership:**
```bash
groups $USER
```

Should show `scanner` or `lp` in the list.

**Check udev Rules:**
```bash
# Create custom udev rule if needed
sudo nano /etc/udev/rules.d/99-scanner.rules
```

Add (replace XXXX:YYYY with your scanner's vendor:product ID from lsusb):
```
ATTRS{idVendor}=="XXXX", ATTRS{idProduct}=="YYYY", MODE="0666", GROUP="scanner"
```

**Reload udev Rules:**
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Scanner Detected but Won't Scan

**Check Backend Support:**
```bash
scanimage --help
```

**Test with Simple Scan:**
```bash
scanimage --test
```

**Check Scanner Options:**
```bash
scanimage -A
```

### Network Scanner Issues

**Test Network Connection:**
```bash
ping scanner.local
```

**Check saned Service:**
```bash
sudo systemctl status saned
```

**Verify Firewall:**
```bash
# Allow SANE port 6566
sudo ufw allow 6566/tcp
```

## Additional Resources

- **SANE Documentation**: http://www.sane-project.org/
- **SANE Supported Devices**: http://www.sane-project.org/sane-mfgs.html
- **Xerox Scanner Support**: Check Xerox website for specific D35 information
- **Ubuntu Scanner Setup**: https://help.ubuntu.com/community/Scanners

## Testing Your Setup

Once configured, test your scanner:

1. **Quick Test:**
   ```bash
   python3 setup_check.py
   ```

2. **GUI Test:**
   ```bash
   python3 scanner_app.py
   ```

3. **CLI Test:**
   ```bash
   python3 scanner_cli.py --list
   ```

If you see your scanner listed, you're ready to scan!

## Getting Help

If you continue to experience issues:

1. Check the SANE documentation for your specific scanner model
2. Search the SANE mailing list archives
3. Open an issue on this repository with:
   - Your operating system and version
   - Output of `scanimage -L`
   - Output of `lsusb` (Linux) or `system_profiler SPUSBDataType` (macOS)
   - Any error messages you're receiving
