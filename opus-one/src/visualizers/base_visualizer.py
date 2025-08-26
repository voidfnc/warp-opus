"""
Base Visualizer Class for Opus One
Provides common functionality for all visualizers
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient
import numpy as np
from typing import Optional, Dict, Any, List
from abc import abstractmethod


class BaseVisualizer(QWidget):
    """Abstract base class for all visualizers"""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    transition_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Audio engine reference
        self.audio_engine = None
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.fps = 60
        
        # Transition properties
        self._opacity = 1.0
        self.transition_animation = QPropertyAnimation(self, b"opacity")
        self.transition_animation.setDuration(500)
        self.transition_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Common visual properties
        self.theme = self.get_default_theme()
        
        # Performance metrics
        self.frame_count = 0
        self.last_fps_update = 0
        
        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Initialize visualizer-specific components
        self.initialize()
        
    @abstractmethod
    def initialize(self):
        """Initialize visualizer-specific components"""
        pass
        
    @abstractmethod
    def render_visualization(self, painter: QPainter):
        """Render the visualization - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def process_audio_data(self):
        """Process audio data for visualization - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """Return the display name of this visualizer"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of this visualizer"""
        pass
    
    def set_audio_engine(self, audio_engine):
        """Set the audio engine for data source"""
        self.audio_engine = audio_engine
    
    def start_visualization(self):
        """Start the visualization animation"""
        self.timer.start(int(1000 / self.fps))
    
    def stop_visualization(self):
        """Stop the visualization animation"""
        self.timer.stop()
    
    def update_visualization(self):
        """Update visualization data and trigger repaint"""
        if self.audio_engine:
            self.process_audio_data()
        self.update()
    
    def paintEvent(self, event):
        """Main paint event handler"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Apply opacity for transitions
        painter.setOpacity(self._opacity)
        
        # Render the visualization
        self.render_visualization(painter)
        
        # Update frame counter
        self.frame_count += 1
    
    def transition_in(self, duration=500):
        """Animate the visualizer appearing"""
        self.transition_animation.setDuration(duration)
        self.transition_animation.setStartValue(0.0)
        self.transition_animation.setEndValue(1.0)
        self.transition_animation.finished.connect(lambda: self.transition_complete.emit())
        self.transition_animation.start()
    
    def transition_out(self, duration=500):
        """Animate the visualizer disappearing"""
        self.transition_animation.setDuration(duration)
        self.transition_animation.setStartValue(1.0)
        self.transition_animation.setEndValue(0.0)
        self.transition_animation.finished.connect(lambda: self.transition_complete.emit())
        self.transition_animation.start()
    
    def get_opacity(self):
        """Get current opacity"""
        return self._opacity
    
    def set_opacity(self, value):
        """Set opacity for transitions"""
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def apply_theme(self, theme: Dict[str, Any]):
        """Apply a theme to the visualizer"""
        self.theme = theme
        self.update()
    
    def get_default_theme(self) -> Dict[str, Any]:
        """Get the default theme"""
        return {
            'colors': {
                'primary': QColor(138, 43, 226),    # Blue Violet
                'secondary': QColor(75, 0, 130),     # Indigo
                'accent': QColor(255, 20, 147),      # Deep Pink
                'background': QColor(20, 20, 40),    # Dark background
                'text': QColor(255, 255, 255),       # White text
            },
            'gradients': {
                'spectrum': [
                    QColor(138, 43, 226),
                    QColor(75, 0, 130),
                    QColor(255, 20, 147),
                    QColor(255, 105, 180),
                    QColor(255, 192, 203),
                ]
            },
            'effects': {
                'glow_intensity': 0.8,
                'particle_density': 1.0,
                'blur_amount': 0.5,
            }
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings for this visualizer"""
        return {}
    
    def apply_settings(self, settings: Dict[str, Any]):
        """Apply settings to this visualizer"""
        pass
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_visualization()
        if self.transition_animation:
            self.transition_animation.stop()
    
    # Utility methods for common operations
    
    def create_gradient(self, colors: List[QColor], start_point, end_point) -> QLinearGradient:
        """Create a linear gradient from a list of colors"""
        gradient = QLinearGradient(start_point, end_point)
        if len(colors) == 1:
            gradient.setColorAt(0, colors[0])
            gradient.setColorAt(1, colors[0])
        else:
            for i, color in enumerate(colors):
                position = i / (len(colors) - 1)
                gradient.setColorAt(position, color)
        return gradient
    
    def create_radial_gradient(self, colors: List[QColor], center, radius) -> QRadialGradient:
        """Create a radial gradient from a list of colors"""
        gradient = QRadialGradient(center, radius)
        if len(colors) == 1:
            gradient.setColorAt(0, colors[0])
            gradient.setColorAt(1, colors[0])
        else:
            for i, color in enumerate(colors):
                position = i / (len(colors) - 1)
                gradient.setColorAt(position, color)
        return gradient
    
    def map_value(self, value: float, in_min: float, in_max: float, 
                  out_min: float, out_max: float) -> float:
        """Map a value from one range to another"""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def get_color_from_gradient(self, value: float, colors: List[QColor]) -> QColor:
        """Get a color from a gradient based on a value between 0 and 1"""
        if not colors:
            return QColor(255, 255, 255)
        
        if len(colors) == 1:
            return colors[0]
        
        value = max(0, min(1, value))  # Clamp between 0 and 1
        
        # Find which two colors to interpolate between
        segment = value * (len(colors) - 1)
        index = int(segment)
        fraction = segment - index
        
        if index >= len(colors) - 1:
            return colors[-1]
        
        # Interpolate between the two colors
        color1 = colors[index]
        color2 = colors[index + 1]
        
        r = int(color1.red() * (1 - fraction) + color2.red() * fraction)
        g = int(color1.green() * (1 - fraction) + color2.green() * fraction)
        b = int(color1.blue() * (1 - fraction) + color2.blue() * fraction)
        
        return QColor(r, g, b)
