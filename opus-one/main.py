#!/usr/bin/env python3
"""
Opus One - Beautiful Audio Visualizer
A modern, minimalistic audio visualizer with smooth animations
Created with PyQt6 and Python 3.13
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon, QFont, QFontDatabase
from ui.main_window import MainWindow
import logging
from datetime import datetime

# Configure logging
def setup_logging():
    """Configure application logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"opus_one_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Opus One Audio Visualizer")
    
    # Create Qt Application
    # Qt6 has high DPI scaling enabled by default
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Opus One")
    app.setApplicationDisplayName("Opus One - Audio Visualizer")
    app.setOrganizationName("VipeoTech")
    app.setOrganizationDomain("vipeotech.com")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Load custom fonts if available
    font_dir = Path("assets/fonts")
    if font_dir.exists():
        for font_file in font_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))
            logger.info(f"Loaded font: {font_file.name}")
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run application
        logger.info("Application started successfully")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
