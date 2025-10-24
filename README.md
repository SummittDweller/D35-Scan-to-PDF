# D35-Scan-to-PDF

A Python Flet-based GUI application for scanning documents using a Xerox D35 scanner and saving them as multi-page PDF files.

## Features

- 🖨️ **Scanner Detection**: Automatically detects available SANE-compatible scanners
- 📄 **Multi-Page Scanning**: Scan multiple pages one at a time
- 📑 **PDF Generation**: Combine all scanned pages into a single multi-page PDF
- ⚙️ **Configurable Settings**: Adjust resolution (150/300/600 DPI) and scan mode (Color/Gray/Lineart)
- 🎨 **Modern UI**: Clean and intuitive Flet-based graphical interface
- 💾 **Organized Output**: Automatically saves PDFs with timestamps in a `scans/` directory

## Requirements

### System Requirements

- Python 3.8 or higher
- SANE (Scanner Access Now Easy) backend installed on your system
- Xerox D35 scanner connected and configured

### Linux Installation

For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install sane sane-utils libsane-dev python3-dev
```

For Fedora/RHEL:
```bash
sudo dnf install sane-backends sane-backends-drivers-scanners
```

### macOS Installation

```bash
brew install sane-backends
```

### Windows Installation

Windows support for SANE is limited. Consider using:
- WIA (Windows Image Acquisition) alternatives
- Or run in WSL2 with USB passthrough

## Installation

1. Clone this repository:
```bash
git clone https://github.com/SummittDweller/D35-Scan-to-PDF.git
cd D35-Scan-to-PDF
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Verify your scanner is detected by SANE:
```bash
scanimage -L
```

## Usage

1. Run the application:
```bash
python scanner_app.py
```

2. Using the application:
   - Click **"Refresh Scanners"** to detect available scanners
   - Select your Xerox D35 from the dropdown menu
   - Configure your preferred **Resolution** and **Scan Mode**
   - Click **"Scan Page"** to scan each page (repeat for multiple pages)
   - Click **"Save as PDF"** to create a multi-page PDF file
   - Use **"Clear Scans"** to start over if needed

3. Find your scanned PDFs in the `scans/` directory with timestamp-based filenames (e.g., `scan_20231024_153045.pdf`)

## Configuration

The application uses the following default settings:
- **Resolution**: 300 DPI (adjustable to 150 or 600 DPI)
- **Scan Mode**: Color (adjustable to Gray or Lineart)
- **Output Directory**: `./scans/`

## Troubleshooting

### Scanner Not Detected

1. Verify scanner is connected and powered on
2. Check SANE can detect it:
   ```bash
   scanimage -L
   ```
3. You may need to configure SANE backend for your specific scanner model
4. Check scanner permissions:
   ```bash
   ls -l /dev/bus/usb/*/*
   ```
   
### Permission Issues

If you get permission errors, add your user to the scanner group:
```bash
sudo usermod -a -G scanner $USER
# Or on some systems:
sudo usermod -a -G lp $USER
```

Then log out and back in for changes to take effect.

### SANE Configuration

Edit `/etc/sane.d/dll.conf` to ensure appropriate backends are enabled. For Xerox scanners, you might need:
- `xerox_mfp`
- `net` (for network scanners)

## Project Structure

```
D35-Scan-to-PDF/
├── scanner_app.py       # Main application file
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── scans/              # Output directory (created automatically)
```

## Dependencies

- **flet**: Modern Python UI framework
- **python-sane**: Python bindings for SANE scanner interface
- **Pillow**: Image processing library
- **reportlab**: PDF generation library

## License

This project is open source. See the repository for license details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

SummittDweller

## Acknowledgments

- Built with [Flet](https://flet.dev/) - Flutter apps in Python
- Uses [SANE](http://www.sane-project.org/) for scanner access
- PDF generation with [ReportLab](https://www.reportlab.com/)
