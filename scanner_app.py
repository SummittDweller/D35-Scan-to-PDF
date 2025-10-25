"""
D35 Scanner to PDF Application
A Flet-based GUI application for scanning documents using Apple's Image Capture
and saving them as multi-page PDF files with timestamped filenames.
"""

import flet as ft
import subprocess
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
from datetime import datetime
import traceback
import time
import glob
import shutil


class ScannerApp:
    """Main application class for the D35 Scanner to PDF app using Image Capture."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "D35 Scanner to PDF (Image Capture)"
        self.page.window_width = 600
        self.page.window_height = 700
        self.page.padding = 20
        
        self.scanner_devices = []
        self.selected_device = None
        self.scanned_images = []
        self.scan_dir = None
        self.scan_counter = 0
        
        # UI Components
        self.status_text = ft.Text("Ready", size=16, color=ft.colors.GREEN)
        self.scanner_dropdown = ft.Dropdown(
            label="Select Scanner",
            width=500,
            on_change=self.on_scanner_selected
        )
        self.scan_count_text = ft.Text("Scanned pages: 0", size=14)
        self.refresh_btn = ft.ElevatedButton(
            "Refresh Scanners",
            icon=ft.icons.REFRESH,
            on_click=self.refresh_scanners
        )
        self.scan_btn = ft.ElevatedButton(
            "Scan Page",
            icon=ft.icons.SCANNER,
            on_click=self.scan_page,
            disabled=True
        )
        self.save_pdf_btn = ft.ElevatedButton(
            "Save as PDF",
            icon=ft.icons.PICTURE_AS_PDF,
            on_click=self.save_as_pdf,
            disabled=True
        )
        self.clear_btn = ft.ElevatedButton(
            "Clear Scans",
            icon=ft.icons.CLEAR,
            on_click=self.clear_scans,
            disabled=True
        )
        self.progress_bar = ft.ProgressBar(visible=False)
        
        # Resolution settings
        self.resolution_dropdown = ft.Dropdown(
            label="Resolution (DPI)",
            width=200,
            value="300",
            options=[
                ft.dropdown.Option("150"),
                ft.dropdown.Option("300"),
                ft.dropdown.Option("600"),
            ]
        )
        
        # Color mode settings
        self.mode_dropdown = ft.Dropdown(
            label="Scan Mode",
            width=200,
            value="Color",
            options=[
                ft.dropdown.Option("Color"),
                ft.dropdown.Option("Gray"),
                ft.dropdown.Option("Lineart"),
            ]
        )
        
        self.build_ui()
        self.refresh_scanners(None)
    
    def build_ui(self):
        """Build the user interface."""
        self.page.add(
            ft.Column([
                ft.Text("D35 Scanner to PDF (Image Capture)", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Status section
                ft.Container(
                    content=self.status_text,
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                ),
                
                # Scanner selection
                ft.Row([
                    self.scanner_dropdown,
                    self.refresh_btn,
                ]),
                
                # Scan settings
                ft.Row([
                    self.resolution_dropdown,
                    self.mode_dropdown,
                ]),
                
                # Progress bar
                self.progress_bar,
                
                # Scan count
                self.scan_count_text,
                
                # Action buttons
                ft.Row([
                    self.scan_btn,
                    self.clear_btn,
                ]),
                
                ft.Row([
                    self.save_pdf_btn,
                ]),
                
                ft.Divider(),
                
                # Instructions
                ft.Container(
                    content=ft.Column([
                        ft.Text("Instructions:", weight=ft.FontWeight.BOLD),
                        ft.Text("1. Connect your D35 scanner and ensure it's powered on"),
                        ft.Text("2. Click 'Refresh Scanners' to detect available scanning methods"),
                        ft.Text("3. Select a scanning option from the dropdown:"),
                        ft.Text("   • AppleScript: Automated Image Capture control"),
                        ft.Text("   • Manual Import: Scan with Image Capture app, save to Desktop"),
                        ft.Text("4. Configure resolution and scan mode"),
                        ft.Text("5. Click 'Scan Page' for each page you want to scan"),
                        ft.Text("6. For Manual Import: Use Image Capture app to scan and save to Desktop"),
                        ft.Text("7. Click 'Save as PDF' to create a timestamped PDF file"),
                        ft.Text(""),
                        ft.Text("Note: This app works with Apple's Image Capture system.", 
                               style=ft.TextThemeStyle.BODY_SMALL, 
                               color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Text("PDFs are saved as 'Scan_YYYYMMDD_HHMMSS.pdf' in the 'scans' folder.",
                               style=ft.TextThemeStyle.BODY_SMALL, 
                               color=ft.colors.ON_SURFACE_VARIANT),
                        ft.Text("For best results with D35, use the Manual Import method.",
                               style=ft.TextThemeStyle.BODY_SMALL, 
                               color=ft.colors.ON_SURFACE_VARIANT),
                    ]),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                ),
            ])
        )
    
    def update_status(self, message: str, color: str = ft.colors.GREEN):
        """Update the status message."""
        self.status_text.value = message
        self.status_text.color = color
        self.page.update()
    
    def refresh_scanners(self, e):
        """Refresh the list of available scanners using macOS Image Capture."""
        try:
            self.update_status("Checking for Image Capture support...", ft.colors.BLUE)
            
            self.scanner_dropdown.options.clear()
            self.scanner_devices.clear()
            
            # Check for imagecapture command first
            ic_result = subprocess.run(['which', 'imagecapture'], capture_output=True, text=True)
            
            if ic_result.returncode == 0:
                # imagecapture command is available
                try:
                    ic_list_result = subprocess.run([
                        'imagecapture', '-list'
                    ], capture_output=True, text=True, timeout=5)
                    
                    if ic_list_result.returncode == 0 and ic_list_result.stdout.strip():
                        lines = ic_list_result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip() and not line.startswith('Devices:'):
                                device_name = line.strip()
                                device_entry = {
                                    'id': f'ic_{device_name.replace(" ", "_")}',
                                    'name': f'Image Capture: {device_name}',
                                    'type': 'scanner'
                                }
                                self.scanner_devices.append(device_entry)
                                self.scanner_dropdown.options.append(
                                    ft.dropdown.Option(
                                        key=device_entry['id'], 
                                        text=device_entry['name']
                                    )
                                )
                except subprocess.TimeoutExpired:
                    pass  # Fall back to generic option
            
            # Always add a generic option that uses AppleScript as fallback
            device_entry = {
                'id': 'image_capture_applescript',
                'name': 'Image Capture (AppleScript)',
                'type': 'scanner'
            }
            self.scanner_devices.append(device_entry)
            self.scanner_dropdown.options.append(
                ft.dropdown.Option(
                    key=device_entry['id'], 
                    text=device_entry['name']
                )
            )
            
            # Add manual option
            device_entry = {
                'id': 'manual_import',
                'name': 'Manual Import (from Desktop)',
                'type': 'manual'
            }
            self.scanner_devices.append(device_entry)
            self.scanner_dropdown.options.append(
                ft.dropdown.Option(
                    key=device_entry['id'], 
                    text=device_entry['name']
                )
            )
            
            self.update_status(f"Found {len(self.scanner_devices)} scanning option(s)", ft.colors.GREEN)
            self.page.update()
            
        except Exception as ex:
            self.update_status(f"Error: {str(ex)}", ft.colors.RED)
            print(traceback.format_exc())
    
    def on_scanner_selected(self, e):
        """Handle scanner selection."""
        if self.scanner_dropdown.value:
            try:
                # Find the selected device
                self.selected_device = None
                for device in self.scanner_devices:
                    if device['id'] == self.scanner_dropdown.value:
                        self.selected_device = device
                        break
                
                if self.selected_device:
                    self.scan_btn.disabled = False
                    self.update_status("Scanner ready - using Image Capture", ft.colors.GREEN)
                    self.page.update()
                else:
                    self.scan_btn.disabled = True
                    self.update_status("Invalid scanner selection", ft.colors.RED)
                    self.page.update()
                
            except Exception as ex:
                self.update_status(f"Error selecting scanner: {str(ex)}", ft.colors.RED)
                print(traceback.format_exc())
                self.scan_btn.disabled = True
                self.page.update()
    
    def scan_page(self, e):
        """Scan a single page using the selected method."""
        if not self.selected_device:
            self.update_status("No scanner selected", ft.colors.RED)
            return
        
        try:
            self.progress_bar.visible = True
            self.scan_btn.disabled = True
            self.update_status("Initiating scan...", ft.colors.BLUE)
            self.page.update()
            
            # Create temp directory if needed
            if not self.scan_dir:
                self.scan_dir = tempfile.mkdtemp(prefix="d35_scan_")
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            
            scanned_file_path = None
            
            if self.selected_device['id'] == 'manual_import':
                scanned_file_path = self.handle_manual_import(timestamp)
            elif self.selected_device['id'] == 'image_capture_applescript':
                scanned_file_path = self.handle_applescript_scan(timestamp)
            elif self.selected_device['id'].startswith('ic_'):
                scanned_file_path = self.handle_imagecapture_cmd(timestamp)
            else:
                raise Exception(f"Unknown scanner type: {self.selected_device['id']}")
            
            if not scanned_file_path:
                raise Exception("No scanned file was obtained")
            
            # Convert to PNG and add to list
            png_path = os.path.join(self.scan_dir, f"scan_{len(self.scanned_images):03d}.png")
            
            if not scanned_file_path.lower().endswith('.png'):
                with Image.open(scanned_file_path) as img:
                    img.save(png_path)
                if scanned_file_path != png_path and os.path.exists(scanned_file_path):
                    os.remove(scanned_file_path)
            else:
                if scanned_file_path != png_path:
                    os.rename(scanned_file_path, png_path)
            
            self.scanned_images.append(png_path)
            
            # Update UI
            self.scan_count_text.value = f"Scanned pages: {len(self.scanned_images)}"
            self.save_pdf_btn.disabled = False
            self.clear_btn.disabled = False
            self.update_status(f"Page {len(self.scanned_images)} scanned successfully", ft.colors.GREEN)
            
        except Exception as ex:
            self.update_status(f"Scan error: {str(ex)}", ft.colors.RED)
            print(traceback.format_exc())
        
        finally:
            self.progress_bar.visible = False
            self.scan_btn.disabled = False
            self.page.update()
    
    def handle_manual_import(self, timestamp):
        """Handle manual import from Desktop."""
        self.update_status("Please scan with Image Capture app and save to Desktop...", ft.colors.BLUE)
        self.page.update()
        
        # Look for new files on Desktop
        desktop_path = os.path.expanduser("~/Desktop")
        
        # Get initial file list
        initial_files = set(os.listdir(desktop_path))
        
        self.update_status("Waiting for new scan file on Desktop (30 seconds)...", ft.colors.ORANGE)
        self.page.update()
        
        # Wait for new file to appear
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            current_files = set(os.listdir(desktop_path))
            new_files = current_files - initial_files
            
            # Look for image files
            for new_file in new_files:
                if new_file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.tiff', '.tif')):
                    source_path = os.path.join(desktop_path, new_file)
                    dest_path = os.path.join(self.scan_dir, f"temp_{timestamp}.{new_file.split('.')[-1]}")
                    
                    # Copy the file
                    shutil.copy2(source_path, dest_path)
                    
                    self.update_status(f"Found scan: {new_file}", ft.colors.GREEN)
                    return dest_path
        
        raise Exception("No new scan file found on Desktop within 30 seconds")
    
    def handle_applescript_scan(self, timestamp):
        """Handle scanning using AppleScript to control Image Capture."""
        applescript = '''
        tell application "Image Capture"
            activate
            delay 2
            try
                scan
                delay 3
                return "scan_initiated"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
        '''
        
        self.update_status("Opening Image Capture app...", ft.colors.BLUE)
        self.page.update()
        
        try:
            result = subprocess.run([
                'osascript', '-e', applescript
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "scan_initiated" in result.stdout:
                # After AppleScript, fall back to manual detection
                return self.handle_manual_import(timestamp)
            else:
                self.update_status("AppleScript failed, please use Image Capture manually", ft.colors.ORANGE)
                return self.handle_manual_import(timestamp)
                
        except subprocess.TimeoutExpired:
            self.update_status("AppleScript timeout, please use Image Capture manually", ft.colors.ORANGE)
            return self.handle_manual_import(timestamp)
    
    def handle_imagecapture_cmd(self, timestamp):
        """Handle scanning using imagecapture command (if available)."""
        temp_filename = f"scan_{timestamp}"
        
        cmd = [
            'imagecapture',
            '-path', self.scan_dir,
            '-name', temp_filename,
            '-type', 'public.jpeg',
            '-dpi', str(int(self.resolution_dropdown.value))
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"Image Capture command failed: {result.stderr}")
        
        # Find the scanned file
        pattern = os.path.join(self.scan_dir, f"{temp_filename}*")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            # Try alternative patterns
            pattern = os.path.join(self.scan_dir, "*.jp*")
            all_files = glob.glob(pattern)
            if all_files:
                matching_files = [max(all_files, key=os.path.getmtime)]
        
        if not matching_files:
            raise Exception("No scanned image file found")
        
        return matching_files[0]
    
    def save_as_pdf(self, e):
        """Save all scanned pages as a multi-page PDF with timestamped filename."""
        if not self.scanned_images:
            self.update_status("No scanned pages to save", ft.colors.ORANGE)
            return
        
        try:
            self.progress_bar.visible = True
            self.save_pdf_btn.disabled = True
            self.update_status("Creating PDF...", ft.colors.BLUE)
            self.page.update()
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "scans"
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp (replacing "Scan.pdf" with timestamped version)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = os.path.join(output_dir, f"Scan_{timestamp}.pdf")
            
            # Create PDF
            first_image = Image.open(self.scanned_images[0])
            img_width, img_height = first_image.size
            
            # Calculate page size based on first image
            # Convert pixels to points (1 inch = 72 points)
            dpi = int(self.resolution_dropdown.value)
            page_width = (img_width / dpi) * 72
            page_height = (img_height / dpi) * 72
            
            c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))
            
            for idx, image_path in enumerate(self.scanned_images):
                img = Image.open(image_path)
                img_reader = ImageReader(img)
                
                # Draw image on canvas
                c.drawImage(img_reader, 0, 0, width=page_width, height=page_height)
                
                if idx < len(self.scanned_images) - 1:
                    c.showPage()
            
            c.save()
            
            self.update_status(
                f"PDF saved: Scan_{timestamp}.pdf ({len(self.scanned_images)} pages)",
                ft.colors.GREEN
            )
            
        except Exception as ex:
            self.update_status(f"Error saving PDF: {str(ex)}", ft.colors.RED)
            print(traceback.format_exc())
        
        finally:
            self.progress_bar.visible = False
            self.save_pdf_btn.disabled = False
            self.page.update()
    
    def clear_scans(self, e):
        """Clear all scanned pages."""
        try:
            # Clean up temporary files
            if self.scan_dir and os.path.exists(self.scan_dir):
                for image_path in self.scanned_images:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                os.rmdir(self.scan_dir)
            
            self.scanned_images.clear()
            self.scan_dir = None
            self.scan_count_text.value = "Scanned pages: 0"
            self.save_pdf_btn.disabled = True
            self.clear_btn.disabled = True
            self.update_status("Scans cleared", ft.colors.GREEN)
            self.page.update()
            
        except Exception as ex:
            self.update_status(f"Error clearing scans: {str(ex)}", ft.colors.RED)
            print(traceback.format_exc())


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    ScannerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
