"""
FFmpeg setup for Opus One Audio Visualizer
Configures pydub to find FFmpeg
"""

import os
import sys
from pathlib import Path
from pydub.utils import which

def setup_ffmpeg():
    """Configure FFmpeg path for pydub"""
    # Try to find FFmpeg in various locations
    possible_paths = []
    
    # Check if running from compiled executable
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        base_path = Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent)
        possible_paths.extend([
            base_path / 'ffmpeg' / 'ffmpeg.exe',
            base_path / 'ffmpeg.exe',
            base_path.parent / 'ffmpeg' / 'ffmpeg.exe',
        ])
    else:
        # Running from Python script
        base_path = Path(__file__).parent.parent.parent  # Go to project root
        possible_paths.extend([
            base_path / 'ffmpeg' / 'ffmpeg.exe',
            base_path / 'dist' / 'OpusOne' / 'ffmpeg' / 'ffmpeg.exe',
        ])
    
    # Add system paths
    possible_paths.extend([
        Path('C:/ffmpeg/bin/ffmpeg.exe'),
        Path('C:/Program Files/ffmpeg/bin/ffmpeg.exe'),
        Path('C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe'),
    ])
    
    # Check each path
    for path in possible_paths:
        if path.exists():
            # Set the path for pydub
            from pydub import AudioSegment
            from pydub.utils import which
            
            # Set FFmpeg path
            AudioSegment.converter = str(path)
            os.environ['FFMPEG_BINARY'] = str(path)
            
            # Also set ffprobe if it exists
            ffprobe_path = path.parent / 'ffprobe.exe'
            if ffprobe_path.exists():
                AudioSegment.ffprobe = str(ffprobe_path)
                os.environ['FFPROBE_BINARY'] = str(ffprobe_path)
            
            print(f"FFmpeg configured: {path}")
            return True
    
    # Try system PATH
    if which("ffmpeg"):
        print("Using FFmpeg from system PATH")
        return True
    
    print("Warning: FFmpeg not found. MP3 support may not work.")
    return False

# Auto-setup when imported
setup_ffmpeg()
