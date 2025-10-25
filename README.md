# D35-Scan-to-PDF

A Python Flet-based GUI application for scanning documents using a Xerox D35 scanner and Apple's Image Capture, saving them as multi-page PDF files with timestamped filenames.

## Features

- 🖨️ **Scanner Detection**: Uses Apple's Image Capture for seamless macOS scanner integration
- 📄 **Multi-Page Scanning**: Scan multiple pages one at a time
- 📑 **PDF Generation**: Combine all scanned pages into a single multi-page PDF
- ⚙️ **Configurable Settings**: Adjust resolution (150/300/600 DPI) and scan mode (Color/Gray/Lineart)
- 🎨 **Modern UI**: Clean and intuitive Flet-based graphical interface
- 💾 **Organized Output**: Automatically saves PDFs with timestamps as `Scan_YYYYMMDD_HHMMSS.pdf` in a `scans/` directory
- 🍎 **macOS Native**: Uses Apple's Image Capture for better compatibility and reliability

## Requirements

### System Requirements

- **macOS** (required for Image Capture integration)
- Python 3.8 or higher
- Apple's Image Capture (built into macOS)
- Xerox D35 scanner connected via USB

### Why Image Capture?

This app has been updated to use Apple's native Image Capture instead of SANE because:
- Better compatibility with modern macOS versions
- More reliable scanner detection and communication
- No need for complex SANE backend configuration
- Leverages macOS's built-in scanner drivers

## Installation

1. Clone this repository:
```bash
git clone https://github.com/SummittDweller/D35-Scan-to-PDF.git
cd D35-Scan-to-PDF
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Verify Image Capture is available:
```bash
which imagecapture
```

5. Test scanner detection:
```bash
imagecapture -list
```

## Usage

### GUI Application

1. Run the GUI application:
```bash
python scanner_app.py
# or use the launcher script
./run.sh
```

2. Using the GUI:
   - Click **"Refresh Scanners"** to detect available Image Capture compatible devices
   - Select your scanner from the dropdown menu (or use "Auto-detect")
   - Configure your preferred **Resolution** and **Scan Mode**
   - Click **"Scan Page"** to scan each page using Image Capture (repeat for multiple pages)
   - Click **"Save as PDF"** to create a multi-page PDF file
   - Use **"Clear Scans"** to start over if needed

3. Find your scanned PDFs in the `scans/` directory with timestamped filenames following the pattern `Scan_YYYYMMDD_HHMMSS.pdf` (e.g., `Scan_20231024_153045.pdf`)

### Command Line Interface (CLI)

For automation or headless operation, use the CLI tool:

1. List available scanners:
```bash
python scanner_cli.py --list
```

2. Scan pages:
```bash
# Scan 3 pages at 300 DPI in color mode
python scanner_cli.py --pages 3 --resolution 300 --mode Color

# Scan 5 pages in grayscale with custom output
python scanner_cli.py -p 5 -m Gray -o my_document.pdf
```

3. CLI Options:
   - `--list, -l`: List available scanners
   - `--device, -d`: Scanner device name (default: auto-detect)
   - `--pages, -p`: Number of pages to scan (default: 1)
   - `--resolution, -r`: Resolution in DPI (150/300/600, default: 300)
   - `--mode, -m`: Scan mode (Color/Gray/Lineart, default: Color)
   - `--output, -o`: Output PDF filename (optional, defaults to `Scan_TIMESTAMP.pdf`)

## Configuration

The application uses the following default settings:
- **Resolution**: 300 DPI (adjustable to 150 or 600 DPI)
- **Scan Mode**: Color (adjustable to Gray or Lineart)
- **Output Directory**: `./scans/`
- **Filename Pattern**: `Scan_YYYYMMDD_HHMMSS.pdf`

## Troubleshooting

### Scanner Not Detected

1. Verify scanner is connected via USB and powered on
2. Check Image Capture can detect it:
   ```bash
   imagecapture -list
   ```
3. Try opening the macOS "Image Capture" app to verify the scanner works
4. Ensure the scanner is not being used by another application

### Permission Issues

Image Capture should handle permissions automatically, but if you encounter issues:
1. Check System Preferences > Security & Privacy > Privacy > Camera (if applicable)
2. Make sure the Terminal app (or your Python environment) has necessary permissions

### Image Capture Command Not Found

If `imagecapture` command is not available:
1. Ensure you're running on macOS
2. The command should be available at `/usr/bin/imagecapture`
3. Try using the full path: `/usr/bin/imagecapture -list`

### Alternative: Manual Image Capture Integration

If the command-line `imagecapture` tool doesn't work, you can:
1. Use the macOS Image Capture app to scan to a folder
2. Use the app's "Watch Folder" feature to automatically process new scans
3. Set the watched folder to your temp directory

## Project Structure

```
D35-Scan-to-PDF/
├── scanner_app.py       # Main GUI application (Flet)
├── scanner_cli.py       # Command-line interface
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── run.sh              # Launcher script for GUI
├── setup_check.py      # System requirements verification
├── test_scanner_app.py # Unit tests
├── config.example.ini  # Example configuration file
└── scans/              # Output directory (created automatically)
```

## Dependencies

- **flet**: Modern Python UI framework
- **Pillow**: Image processing library
- **reportlab**: PDF generation library
- **Image Capture**: macOS built-in scanning framework (replaces SANE)

## Platform Support

- **macOS**: Full support (primary platform)
- **Linux/Windows**: Not supported in current version due to Image Capture dependency

*Note: For Linux/Windows support, the previous SANE-based version can be found in the git history.*

## License

This project is open source. See the repository for license details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

SummittDweller

## Acknowledgments

- Built with [Flet](https://flet.dev/) - Flutter apps in Python
- Uses Apple's Image Capture for scanner access on macOS
- PDF generation with [ReportLab](https://www.reportlab.com/)
