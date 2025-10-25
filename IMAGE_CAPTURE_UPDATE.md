# D35-Scan-to-PDF: Image Capture Integration Update

## Summary of Changes

This document outlines the changes made to restructure the D35-Scan-to-PDF application to use Apple's Image Capture instead of SANE, and to automatically add timestamps to PDF filenames.

## Key Changes Made

### 1. Replaced SANE with Image Capture Integration

**Before:** Used SANE (Scanner Access Now Easy) for scanner communication
**After:** Uses Apple's Image Capture system for macOS-native scanning

#### Files Modified:
- `scanner_app.py` - Main GUI application
- `scanner_cli.py` - Command-line interface  
- `requirements.txt` - Removed python-sane dependency

#### Technical Changes:
- Removed all `sane` imports and function calls
- Added subprocess calls to `imagecapture` command-line tool
- Added AppleScript integration for Image Capture automation
- Added manual import workflow for desktop file monitoring

### 2. Implemented Timestamped PDF Filenames

**Before:** Generic filenames like `scan_timestamp.pdf`
**After:** Apple-style naming: `Scan_YYYYMMDD_HHMMSS.pdf`

This addresses the original problem where Image Capture creates files named "Scan.pdf" without timestamps.

#### Examples:
- `Scan_20241024_143022.pdf` (October 24, 2024 at 2:30:22 PM)
- `Scan_20241024_143055.pdf` (October 24, 2024 at 2:30:55 PM)

### 3. Added Multiple Scanning Methods

The app now supports three scanning approaches:

#### A. Command-line Image Capture (if available)
- Uses `imagecapture` CLI tool directly
- Automatic scanner detection and control

#### B. AppleScript Automation  
- Uses AppleScript to control Image Capture app
- Falls back to manual method if automation fails

#### C. Manual Import
- User scans with Image Capture app manually
- App monitors Desktop for new scan files
- Automatically imports and processes new files

### 4. Enhanced User Interface

#### Updated Instructions:
- Clear step-by-step guidance for each scanning method
- Specific recommendations for D35 scanner usage
- Better error messaging and status updates

#### New Scanner Selection:
- Dropdown now shows scanning methods instead of just devices
- Options include AppleScript, Manual Import, and auto-detected devices

### 5. Improved Error Handling

- Graceful fallbacks when command-line tools aren't available
- Timeout handling for long-running operations
- Better user feedback for each step of the process

## Usage Workflow

### For GUI Application:

1. **Connect Scanner:** Plug in and power on your D35 scanner
2. **Launch App:** Run `python scanner_app.py`
3. **Refresh Scanners:** Click "Refresh Scanners" to detect methods
4. **Choose Method:** Select from:
   - "Image Capture (AppleScript)" - Automated control
   - "Manual Import (from Desktop)" - Manual scanning (recommended for D35)
5. **Configure Settings:** Set resolution (150/300/600 DPI) and mode (Color/Gray/Lineart)
6. **Scan Pages:** Click "Scan Page" for each page
7. **Save PDF:** Click "Save as PDF" to create timestamped file

### For Manual Import Method:
1. Click "Scan Page" in the app
2. App will prompt and wait for new files
3. Open Image Capture app manually
4. Scan document and save to Desktop
5. App automatically detects and imports the file
6. Repeat for additional pages

### For CLI Application:

```bash
# List available scanning options
python scanner_cli.py --list

# Scan 3 pages at 300 DPI
python scanner_cli.py --pages 3 --resolution 300

# Custom output filename
python scanner_cli.py -p 2 -o "MyDocument.pdf"
```

## Benefits of the New Approach

### 1. Better macOS Integration
- Uses native macOS scanning infrastructure
- No need to install and configure SANE backends
- Works with Apple's existing scanner drivers

### 2. Automatic Timestamp Management
- Solves the "Scan.pdf" overwrite problem
- Each scan gets a unique, timestamped filename
- Maintains chronological order of scans

### 3. Flexible Scanning Options
- Multiple methods accommodate different user preferences
- Fallback options ensure the app works even if some features aren't available
- Manual method provides reliable D35 compatibility

### 4. Simplified Installation
- Fewer dependencies (no more python-sane)
- Works out-of-the-box on macOS
- No complex SANE configuration required

## Compatibility Notes

### Platform Support:
- **macOS:** Full support (primary platform)
- **Linux/Windows:** Not supported in current version due to Image Capture dependency

### macOS Versions:
- Tested on macOS 15.6.1
- Should work on macOS 10.12+ (Image Capture availability)
- Some features may vary by macOS version

### Scanner Compatibility:
- Works with any scanner supported by macOS Image Capture
- Specifically tested workflow for Xerox D35
- Manual import method provides maximum compatibility

## Troubleshooting

### If imagecapture command is not found:
- Use "Manual Import" method instead
- All functionality available through Image Capture app

### If AppleScript fails:
- App automatically falls back to Manual Import
- No user intervention required

### If scanner not detected:
- Check USB connection and power
- Try opening Image Capture app directly to verify scanner works
- Use Manual Import method as reliable fallback

## Testing

A test script `test_imagecapture.py` is included to verify:
- Image Capture command availability
- Python dependency installation
- Basic functionality verification

Run with: `python test_imagecapture.py`

## Future Enhancements

Potential improvements for future versions:
1. Support for network scanners
2. Batch processing of existing scan files
3. OCR integration for searchable PDFs
4. Custom filename templates
5. Integration with cloud storage services