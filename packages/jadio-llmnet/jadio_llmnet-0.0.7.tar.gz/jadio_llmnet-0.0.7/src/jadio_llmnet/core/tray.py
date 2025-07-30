import sys
import threading
from pathlib import Path

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class LLMNetTray:
    def __init__(self):
        if not TRAY_AVAILABLE:
            print("⚠️  System tray not available. Install: pip install pystray pillow")
            return
            
        self.icon = None
        self.running = False
        
    def create_image(self, color='green'):
        # Create a simple colored circle icon
        img = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(img)
        
        colors = {
            'green': '#00ff00',
            'red': '#ff0000',
            'yellow': '#ffff00'
        }
        
        draw.ellipse((8, 8, 56, 56), fill=colors.get(color, '#808080'))
        return img
    
    def run(self):
        if not TRAY_AVAILABLE:
            return
            
        def on_status(icon, item):
            from jadio_llmnet.core.manager import load_config
            try:
                config = load_config()
                assignments = config.get("assigned", {})
                if assignments:
                    print(f"✅ LLMNet Running - {len(assignments)} models assigned")
                else:
                    print("✅ LLMNet Running - No models assigned")
            except:
                print("❌ Could not load status")
        
        def on_quit(icon, item):
            icon.stop()
            self.running = False
            
        menu = Menu(
            MenuItem('Status', on_status),
            MenuItem('Quit', on_quit)
        )
        
        self.icon = Icon('LLMNet', self.create_image(), menu=menu)
        self.running = True
        
        # Run in thread
        thread = threading.Thread(target=self.icon.run)
        thread.daemon = True
        thread.start()
        
    def update_status(self, status='running'):
        if not TRAY_AVAILABLE or not self.icon:
            return
            
        colors = {
            'running': 'green',
            'error': 'red',
            'loading': 'yellow'
        }
        
        self.icon.icon = self.create_image(colors.get(status, 'green'))