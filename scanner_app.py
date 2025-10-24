"""
D35 Scanner to PDF Application
A Flet-based GUI application for scanning documents using a Xerox D35 scanner
and saving them as multi-page PDF files.
"""

import flet as ft
import sane
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import tempfile
from datetime import datetime
import traceback


class ScannerApp:
    """Main application class for the D35 Scanner to PDF app."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "D35 Scanner to PDF"
        self.page.window_width = 600
        self.page.window_height = 700
        self.page.padding = 20
        
        self.scanner = None
        self.scanned_images = []
        self.scan_dir = None
        
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
                ft.Text("Xerox D35 Scanner to PDF", size=24, weight=ft.FontWeight.BOLD),
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
                        ft.Text("1. Select your Xerox D35 scanner from the dropdown"),
                        ft.Text("2. Configure resolution and scan mode"),
                        ft.Text("3. Click 'Scan Page' to scan each page"),
                        ft.Text("4. Repeat step 3 for each page you want to scan"),
                        ft.Text("5. Click 'Save as PDF' to create the multi-page PDF"),
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
        """Refresh the list of available scanners."""
        try:
            self.update_status("Scanning for devices...", ft.colors.BLUE)
            sane.init()
            devices = sane.get_devices()
            
            self.scanner_dropdown.options.clear()
            
            if devices:
                for device in devices:
                    # device is a tuple: (name, vendor, model, type)
                    device_name = f"{device[1]} {device[2]} ({device[0]})"
                    self.scanner_dropdown.options.append(
                        ft.dropdown.Option(key=device[0], text=device_name)
                    )
                self.update_status(f"Found {len(devices)} scanner(s)", ft.colors.GREEN)
            else:
                self.update_status("No scanners found", ft.colors.ORANGE)
            
            self.page.update()
            
        except Exception as ex:
            self.update_status(f"Error: {str(ex)}", ft.colors.RED)
            print(traceback.format_exc())
    
    def on_scanner_selected(self, e):
        """Handle scanner selection."""
        if self.scanner_dropdown.value:
            try:
                # Close previous scanner if open
                if self.scanner:
                    self.scanner.close()
                
                # Open the selected scanner
                self.scanner = sane.open(self.scanner_dropdown.value)
                
                # Try to set some basic options if available
                try:
                    # Set resolution
                    if hasattr(self.scanner, 'resolution'):
                        self.scanner.resolution = int(self.resolution_dropdown.value)
                except:
                    pass
                
                self.scan_btn.disabled = False
                self.update_status("Scanner ready", ft.colors.GREEN)
                self.page.update()
                
            except Exception as ex:
                self.update_status(f"Error opening scanner: {str(ex)}", ft.colors.RED)
                print(traceback.format_exc())
                self.scan_btn.disabled = True
                self.page.update()
    
    def scan_page(self, e):
        """Scan a single page."""
        if not self.scanner:
            self.update_status("No scanner selected", ft.colors.RED)
            return
        
        try:
            self.progress_bar.visible = True
            self.scan_btn.disabled = True
            self.update_status("Scanning...", ft.colors.BLUE)
            self.page.update()
            
            # Create temp directory if needed
            if not self.scan_dir:
                self.scan_dir = tempfile.mkdtemp(prefix="d35_scan_")
            
            # Configure scanner options
            try:
                if hasattr(self.scanner, 'resolution'):
                    self.scanner.resolution = int(self.resolution_dropdown.value)
                
                if hasattr(self.scanner, 'mode'):
                    mode_map = {
                        "Color": "Color",
                        "Gray": "Gray",
                        "Lineart": "Lineart"
                    }
                    self.scanner.mode = mode_map.get(self.mode_dropdown.value, "Color")
            except Exception as ex:
                print(f"Warning: Could not set scanner options: {ex}")
            
            # Perform the scan
            self.scanner.start()
            image = self.scanner.snap()
            
            # Save the scanned image
            image_path = os.path.join(
                self.scan_dir,
                f"scan_{len(self.scanned_images):03d}.png"
            )
            image.save(image_path)
            self.scanned_images.append(image_path)
            
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
    
    def save_as_pdf(self, e):
        """Save all scanned pages as a multi-page PDF."""
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
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = os.path.join(output_dir, f"scan_{timestamp}.pdf")
            
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
                f"PDF saved: {pdf_filename} ({len(self.scanned_images)} pages)",
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
