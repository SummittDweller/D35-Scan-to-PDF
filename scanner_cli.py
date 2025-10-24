#!/usr/bin/env python3
"""
D35 Scanner to PDF - Command Line Interface
Simple CLI tool for scanning documents without the GUI
"""

import sane
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
from datetime import datetime
import argparse
import sys


def list_scanners():
    """List all available SANE scanners."""
    print("Initializing SANE...")
    sane.init()
    devices = sane.get_devices()
    
    if not devices:
        print("No scanners found!")
        return []
    
    print(f"\nFound {len(devices)} scanner(s):\n")
    for i, device in enumerate(devices):
        print(f"  [{i}] {device[1]} {device[2]}")
        print(f"      Device: {device[0]}")
        print(f"      Type: {device[3]}\n")
    
    return devices


def scan_pages(scanner_device, num_pages, resolution=300, mode="Color"):
    """Scan multiple pages."""
    print(f"Opening scanner: {scanner_device}")
    scanner = sane.open(scanner_device)
    
    # Set scanner options
    try:
        if hasattr(scanner, 'resolution'):
            scanner.resolution = resolution
            print(f"Resolution set to {resolution} DPI")
        
        if hasattr(scanner, 'mode'):
            scanner.mode = mode
            print(f"Scan mode set to {mode}")
    except Exception as e:
        print(f"Warning: Could not set all scanner options: {e}")
    
    # Create temporary directory for scans
    temp_dir = tempfile.mkdtemp(prefix="d35_scan_")
    print(f"Temporary directory: {temp_dir}")
    
    scanned_images = []
    
    for page_num in range(1, num_pages + 1):
        print(f"\n--- Scanning page {page_num}/{num_pages} ---")
        input("Press ENTER when ready to scan (or Ctrl+C to cancel)...")
        
        try:
            print("Scanning...")
            scanner.start()
            image = scanner.snap()
            
            # Save the image
            image_path = os.path.join(temp_dir, f"scan_{page_num:03d}.png")
            image.save(image_path)
            scanned_images.append(image_path)
            
            print(f"✓ Page {page_num} scanned successfully")
            
        except Exception as e:
            print(f"✗ Error scanning page {page_num}: {e}")
            break
    
    scanner.close()
    
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
        description="D35 Scanner to PDF - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available scanners
  %(prog)s --list
  
  # Scan 3 pages at 300 DPI
  %(prog)s --device 0 --pages 3 --resolution 300
  
  # Scan in grayscale mode
  %(prog)s -d 0 -p 5 -m Gray
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
        help='Scanner device number or name (use --list to see available devices)'
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
        help='Output PDF filename (default: scan_TIMESTAMP.pdf in scans/ directory)'
    )
    
    args = parser.parse_args()
    
    # Initialize SANE
    try:
        sane.init()
    except Exception as e:
        print(f"Error initializing SANE: {e}")
        print("Make sure SANE is installed and you have permission to access scanners")
        return 1
    
    # List scanners
    if args.list:
        list_scanners()
        return 0
    
    # Validate device argument
    if not args.device:
        print("Error: --device is required (use --list to see available devices)")
        parser.print_help()
        return 1
    
    # Get available devices
    devices = sane.get_devices()
    if not devices:
        print("No scanners found!")
        return 1
    
    # Select device
    scanner_device = None
    if args.device.isdigit():
        device_idx = int(args.device)
        if 0 <= device_idx < len(devices):
            scanner_device = devices[device_idx][0]
        else:
            print(f"Error: Invalid device number {device_idx}")
            list_scanners()
            return 1
    else:
        scanner_device = args.device
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        # Create output directory
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scans")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"scan_{timestamp}.pdf")
    
    print("\n" + "="*60)
    print("D35 Scanner to PDF - CLI")
    print("="*60)
    print(f"Scanner: {scanner_device}")
    print(f"Pages: {args.pages}")
    print(f"Resolution: {args.resolution} DPI")
    print(f"Mode: {args.mode}")
    print(f"Output: {output_file}")
    print("="*60 + "\n")
    
    # Scan pages
    try:
        images, temp_dir = scan_pages(
            scanner_device,
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
