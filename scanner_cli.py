#!/usr/bin/env python3
"""
D35 Scanner to PDF - Command Line Interface
Simple CLI tool for scanning documents using Apple's Image Capture (no GUI)
"""

import subprocess
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
from datetime import datetime
import argparse
import sys
import glob
import time


def list_scanners():
    """List all available Image Capture compatible scanners."""
    print("Checking for Image Capture support...")
    
    # Check if imagecapture command is available
    ic_result = subprocess.run(['which', 'imagecapture'], capture_output=True, text=True)
    
    if ic_result.returncode != 0:
        print("Error: Image Capture command not found!")
        print("Make sure you're running this on macOS with Image Capture installed.")
        return []
    
    print("Image Capture is available.")
    
    # Try to list devices
    try:
        ic_list_result = subprocess.run([
            'imagecapture', '-list'
        ], capture_output=True, text=True, timeout=10)
        
        devices = []
        if ic_list_result.returncode == 0 and ic_list_result.stdout.strip():
            lines = ic_list_result.stdout.strip().split('\n')
            print(f"\nFound scanner devices:\n")
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('Devices:'):
                    device_name = line.strip()
                    devices.append(device_name)
                    print(f"  [{i}] {device_name}")
        else:
            print("No specific devices listed, but Image Capture should auto-detect connected scanners.")
            devices = ["Auto-detect"]
            print("  [0] Auto-detect (Image Capture will find connected scanners)")
        
        return devices
        
    except subprocess.TimeoutExpired:
        print("Timeout while listing devices, but Image Capture should still work.")
        return ["Auto-detect"]
    except Exception as e:
        print(f"Error listing devices: {e}")
        return []


def scan_pages(scanner_device, num_pages, resolution=300, mode="Color"):
    """Scan multiple pages using Image Capture."""
    print(f"Using Image Capture for scanning")
    print(f"Scanner: {scanner_device}")
    print(f"Resolution: {resolution} DPI")
    print(f"Mode: {mode}")
    
    # Create temporary directory for scans
    temp_dir = tempfile.mkdtemp(prefix="d35_scan_")
    print(f"Temporary directory: {temp_dir}")
    
    scanned_images = []
    
    for page_num in range(1, num_pages + 1):
        print(f"\n--- Scanning page {page_num}/{num_pages} ---")
        input("Press ENTER when ready to scan (or Ctrl+C to cancel)...")
        
        try:
            print("Scanning with Image Capture...")
            
            # Generate timestamped filename for this scan
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            temp_filename = f"page_{page_num:03d}_{timestamp}"
            
            # Use imagecapture command to scan
            cmd = [
                'imagecapture',
                '-path', temp_dir,
                '-name', temp_filename,
                '-type', 'public.jpeg',  # Use JPEG for better compatibility
                '-dpi', str(resolution)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"✗ Error scanning page {page_num}: {result.stderr}")
                continue
            
            # Find the scanned file (imagecapture might have added extension)
            pattern = os.path.join(temp_dir, f"{temp_filename}*")
            matching_files = glob.glob(pattern)
            
            if not matching_files:
                # Try to find any recently created files
                all_files = glob.glob(os.path.join(temp_dir, "*"))
                if all_files:
                    # Get the most recently modified file
                    matching_files = [max(all_files, key=os.path.getmtime)]
            
            if not matching_files:
                print(f"✗ No scanned file found for page {page_num}")
                continue
            
            image_path = matching_files[0]
            
            # Convert to PNG if needed and rename consistently
            png_path = os.path.join(temp_dir, f"scan_{page_num:03d}.png")
            
            if not image_path.lower().endswith('.png'):
                with Image.open(image_path) as img:
                    img.save(png_path)
                os.remove(image_path)
            else:
                os.rename(image_path, png_path)
            
            scanned_images.append(png_path)
            print(f"✓ Page {page_num} scanned successfully")
            
        except subprocess.TimeoutExpired:
            print(f"✗ Scan timeout for page {page_num}")
            break
        except Exception as e:
            print(f"✗ Error scanning page {page_num}: {e}")
            break
    
    return scanned_images, temp_dir


def create_pdf(images, output_file, resolution=300):
    """Create a multi-page PDF from scanned images."""
    if not images:
        print("No images to convert!")
        return False
    
    print(f"\nCreating PDF with {len(images)} page(s)...")
    
    try:
        # Get dimensions from first image
        first_image = Image.open(images[0])
        img_width, img_height = first_image.size
        
        # Calculate page size (convert pixels to points)
        page_width = (img_width / resolution) * 72
        page_height = (img_height / resolution) * 72
        
        # Create PDF
        c = canvas.Canvas(output_file, pagesize=(page_width, page_height))
        
        for idx, image_path in enumerate(images):
            print(f"  Adding page {idx + 1}...")
            img = Image.open(image_path)
            img_reader = ImageReader(img)
            
            c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
            
            if idx < len(images) - 1:
                c.showPage()
        
        c.save()
        print(f"\n✓ PDF saved: {output_file}")
        return True
        
    except Exception as e:
        print(f"\n✗ Error creating PDF: {e}")
        return False


def cleanup_temp_files(temp_dir, images):
    """Clean up temporary files."""
    try:
        for image_path in images:
            if os.path.exists(image_path):
                os.remove(image_path)
        
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        print("Temporary files cleaned up")
    except Exception as e:
        print(f"Warning: Could not clean up all temporary files: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="D35 Scanner to PDF - Command Line Interface (Image Capture)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available scanners
  %(prog)s --list
  
  # Scan 3 pages at 300 DPI
  %(prog)s --pages 3 --resolution 300
  
  # Scan in grayscale mode  
  %(prog)s -p 5 -m Gray
        """
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available scanners and exit'
    )
    
    parser.add_argument(
        '--device', '-d',
        type=str,
        default='auto',
        help='Scanner device name (use --list to see available devices, default: auto-detect)'
    )
    
    parser.add_argument(
        '--pages', '-p',
        type=int,
        default=1,
        help='Number of pages to scan (default: 1)'
    )
    
    parser.add_argument(
        '--resolution', '-r',
        type=int,
        default=300,
        choices=[150, 300, 600],
        help='Scan resolution in DPI (default: 300)'
    )
    
    parser.add_argument(
        '--mode', '-m',
        type=str,
        default='Color',
        choices=['Color', 'Gray', 'Lineart'],
        help='Scan mode (default: Color)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output PDF filename (default: Scan_TIMESTAMP.pdf in scans/ directory)'
    )
    
    args = parser.parse_args()
    
    # Check Image Capture availability
    ic_result = subprocess.run(['which', 'imagecapture'], capture_output=True, text=True)
    if ic_result.returncode != 0:
        print("Error: Image Capture command not found!")
        print("Make sure you're running this on macOS with Image Capture installed.")
        return 1
    
    # List scanners
    if args.list:
        list_scanners()
        return 0
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        # Create output directory
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scans")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp (matching Image Capture's "Scan.pdf" but with timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"Scan_{timestamp}.pdf")
    
    print("\n" + "="*60)
    print("D35 Scanner to PDF - CLI (Image Capture)")
    print("="*60)
    print(f"Scanner: {args.device}")
    print(f"Pages: {args.pages}")
    print(f"Resolution: {args.resolution} DPI")
    print(f"Mode: {args.mode}")
    print(f"Output: {output_file}")
    print("="*60 + "\n")
    
    # Scan pages
    try:
        images, temp_dir = scan_pages(
            args.device,
            args.pages,
            args.resolution,
            args.mode
        )
        
        if not images:
            print("No pages were scanned!")
            return 1
        
        # Create PDF
        success = create_pdf(images, output_file, args.resolution)
        
        # Cleanup
        cleanup_temp_files(temp_dir, images)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
