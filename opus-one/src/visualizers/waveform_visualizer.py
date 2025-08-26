"""
Waveform Visualizer for Opus One
Oscilloscope-style waveform display with multiple drawing modes
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath, QPolygonF, QFont
import numpy as np
from collections import deque
from .base_visualizer import BaseVisualizer


class WaveformVisualizer(BaseVisualizer):
    """Oscilloscope-style waveform visualization"""
    
    def initialize(self):
        """Initialize waveform specific components"""
        # Configuration
        self.buffer_size = 512  # Reduced for better performance
        self.history_size = 3  # Reduced history for better performance
        
        # Drawing modes
        self.DRAW_MODE_LINES = 'lines'
        self.DRAW_MODE_DOTS = 'dots'
        self.DRAW_MODE_FILLED = 'filled'
        self.DRAW_MODE_BARS = 'bars'
        self.DRAW_MODE_MIRROR = 'mirror'
        self.current_draw_mode = self.DRAW_MODE_LINES
        
        # Waveform data
        self.waveform_data = np.zeros(self.buffer_size)
        self.waveform_history = deque(maxlen=self.history_size)
        
        # Visual settings
        self.show_grid = True
        self.show_axes = True
        self.persistence = 0.5  # Reduced for performance
        self.line_thickness = 2
        self.dot_size = 3
        self.smooth_factor = 0.3  # Less smoothing for responsiveness
        
        # Trigger settings for stable display
        self.trigger_level = 0.0
        self.trigger_enabled = True
        self.trigger_position = 0.2  # Position on screen (0-1)
        
        # Colors and effects
        self.waveform_color = QColor(0, 255, 128)
        self.grid_color = QColor(50, 50, 70, 100)
        self.axes_color = QColor(100, 100, 120, 150)
        self.glow_enabled = True
        
        # Animation
        self.phase_offset = 0
        self.zoom_level = 1.0
        
        # Override FPS for better performance
        self.fps = 30  # Lower FPS for this visualizer
        
    def get_name(self) -> str:
        return "Waveform"
    
    def get_description(self) -> str:
        return "Oscilloscope-style waveform display"
    
    def process_audio_data(self):
        """Process audio data for waveform visualization"""
        if not self.audio_engine:
            return
        
        try:
            # Get waveform data
            raw_waveform = self.audio_engine.get_waveform_data(self.buffer_size)
            
            # Apply smoothing
            if self.smooth_factor > 0:
                self.waveform_data = (self.waveform_data * self.smooth_factor + 
                                     raw_waveform * (1 - self.smooth_factor))
            else:
                self.waveform_data = raw_waveform
            
            # Find trigger point if enabled
            if self.trigger_enabled:
                trigger_index = self.find_trigger_point()
                if trigger_index > 0:
                    # Shift waveform to align with trigger
                    self.waveform_data = np.roll(self.waveform_data, -trigger_index)
            
            # Add to history for persistence effect
            self.waveform_history.append(self.waveform_data.copy())
            
            # Update phase for animation
            self.phase_offset += 0.02
            if self.phase_offset > 1:
                self.phase_offset = 0
                
        except Exception as e:
            # If audio engine doesn't support waveform, generate from spectrum
            spectrum = self.audio_engine.get_spectrum_data(64)
            # Simple sine synthesis from spectrum
            t = np.linspace(0, 2 * np.pi * 4, self.buffer_size)
            self.waveform_data = np.zeros(self.buffer_size)
            for i, amp in enumerate(spectrum[:16]):  # Use first 16 harmonics
                self.waveform_data += amp * np.sin(t * (i + 1))
            
            # Normalize
            max_val = np.max(np.abs(self.waveform_data))
            if max_val > 0:
                self.waveform_data /= max_val
    
    def find_trigger_point(self) -> int:
        """Find the trigger point in the waveform for stable display"""
        # Look for zero crossing with positive slope
        for i in range(1, len(self.waveform_data) - 1):
            if (self.waveform_data[i-1] <= self.trigger_level and 
                self.waveform_data[i] > self.trigger_level):
                return i
        return 0
    
    def render_visualization(self, painter: QPainter):
        """Render the waveform visualization"""
        width = self.width()
        height = self.height()
        
        # Draw background
        self.draw_background(painter, width, height)
        
        # Draw grid if enabled
        if self.show_grid:
            self.draw_grid(painter, width, height)
        
        # Draw axes if enabled
        if self.show_axes:
            self.draw_axes(painter, width, height)
        
        # Draw historical waveforms with fading
        if self.persistence > 0:
            self.draw_history(painter, width, height)
        
        # Draw current waveform
        self.draw_waveform(painter, width, height, self.waveform_data, 1.0)
        
        # Draw info overlay
        self.draw_info(painter, width, height)
    
    def draw_background(self, painter: QPainter, width, height):
        """Draw background with gradient"""
        gradient = self.create_gradient(
            [QColor(10, 10, 20), QColor(20, 20, 40)],
            QPointF(0, 0),
            QPointF(0, height)
        )
        painter.fillRect(0, 0, width, height, gradient)
    
    def draw_grid(self, painter: QPainter, width, height):
        """Draw oscilloscope grid"""
        painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))
        
        # Vertical lines
        grid_spacing_x = width / 10
        for i in range(11):
            x = i * grid_spacing_x
            painter.drawLine(int(x), 0, int(x), height)
        
        # Horizontal lines
        grid_spacing_y = height / 8
        for i in range(9):
            y = i * grid_spacing_y
            painter.drawLine(0, int(y), width, int(y))
    
    def draw_axes(self, painter: QPainter, width, height):
        """Draw center axes"""
        painter.setPen(QPen(self.axes_color, 2))
        
        # Horizontal center line
        center_y = height / 2
        painter.drawLine(0, int(center_y), width, int(center_y))
        
        # Vertical center line
        center_x = width / 2
        painter.drawLine(int(center_x), 0, int(center_x), height)
    
    def draw_history(self, painter: QPainter, width, height):
        """Draw historical waveforms with fading"""
        for i, historical_waveform in enumerate(self.waveform_history):
            # Calculate opacity based on age
            age_factor = (i + 1) / len(self.waveform_history)
            opacity = self.persistence * age_factor * 0.5
            
            # Draw with reduced opacity
            self.draw_waveform(painter, width, height, historical_waveform, opacity)
    
    def draw_waveform(self, painter: QPainter, width, height, waveform_data, opacity):
        """Draw a single waveform with specified opacity"""
        if len(waveform_data) == 0:
            return
        
        # Set color with opacity
        color = QColor(self.waveform_color)
        color.setAlphaF(opacity)
        
        # Calculate points - sample less for performance
        points = []
        sample_rate = 2 if len(waveform_data) > 256 else 1
        x_step = width / (len(waveform_data) / sample_rate) * self.zoom_level
        center_y = height / 2
        amplitude = height * 0.4
        
        for i in range(0, len(waveform_data), sample_rate):
            x = (i / sample_rate) * x_step
            y = center_y - waveform_data[i] * amplitude
            points.append(QPointF(x, y))
        
        # Draw based on current mode
        if self.current_draw_mode == self.DRAW_MODE_LINES:
            self.draw_lines(painter, points, color)
        elif self.current_draw_mode == self.DRAW_MODE_DOTS:
            self.draw_dots(painter, points, color)
        elif self.current_draw_mode == self.DRAW_MODE_FILLED:
            self.draw_filled(painter, points, color, center_y)
        elif self.current_draw_mode == self.DRAW_MODE_BARS:
            self.draw_bars(painter, points, color, center_y)
        elif self.current_draw_mode == self.DRAW_MODE_MIRROR:
            self.draw_mirror(painter, points, color, center_y, amplitude)
    
    def draw_lines(self, painter: QPainter, points, color):
        """Draw waveform as connected lines"""
        # Skip glow for better performance on lines mode
        if self.glow_enabled and self.persistence < 0.3:
            # Only draw glow when persistence is low
            glow_color = QColor(color)
            glow_color.setAlpha(color.alpha() // 3)
            painter.setPen(QPen(glow_color, self.line_thickness * 2))
            
            path = QPainterPath()
            if points:
                path.moveTo(points[0])
                for point in points[1:]:
                    path.lineTo(point)
            painter.drawPath(path)
        
        # Draw main line
        painter.setPen(QPen(color, self.line_thickness))
        path = QPainterPath()
        if points:
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
        painter.drawPath(path)
    
    def draw_dots(self, painter: QPainter, points, color):
        """Draw waveform as dots"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        # Draw every 4th point for better performance
        for i in range(0, len(points), 4):
            point = points[i]
            # Skip glow for dots mode to improve performance
            painter.drawEllipse(point, self.dot_size, self.dot_size)
    
    def draw_filled(self, painter: QPainter, points, color, center_y):
        """Draw waveform as filled area"""
        if not points:
            return
        
        # Create polygon for filled area
        polygon = QPolygonF()
        polygon.append(QPointF(points[0].x(), center_y))
        for point in points:
            polygon.append(point)
        polygon.append(QPointF(points[-1].x(), center_y))
        
        # Draw with gradient
        gradient = self.create_gradient(
            [color, QColor(color.red(), color.green(), color.blue(), 0)],
            QPointF(0, center_y - 100),
            QPointF(0, center_y)
        )
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(polygon)
        
        # Draw outline
        painter.setPen(QPen(color, self.line_thickness))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        painter.drawPath(path)
    
    def draw_bars(self, painter: QPainter, points, color, center_y):
        """Draw waveform as vertical bars"""
        bar_width = max(2, self.width() / len(points) * 4)
        
        # Draw every 8th bar for much better performance
        for i in range(0, len(points), 8):
            point = points[i]
            bar_height = abs(point.y() - center_y)
            bar_x = point.x()
            bar_y = min(point.y(), center_y)
            
            # Simple fill without gradient for performance
            painter.fillRect(QRectF(bar_x, bar_y, bar_width, bar_height), color)
    
    def draw_mirror(self, painter: QPainter, points, color, center_y, amplitude):
        """Draw waveform with mirrored reflection"""
        if not points:
            return
        
        # Draw upper waveform
        self.draw_lines(painter, points, color)
        
        # Draw mirrored waveform
        mirrored_points = []
        for point in points:
            mirror_y = center_y + (center_y - point.y())
            mirrored_points.append(QPointF(point.x(), mirror_y))
        
        # Draw with reduced opacity
        mirror_color = QColor(color)
        mirror_color.setAlpha(color.alpha() // 2)
        self.draw_lines(painter, mirrored_points, mirror_color)
    
    def draw_info(self, painter: QPainter, width, height):
        """Draw info overlay"""
        # Mode indicator
        painter.setPen(QPen(QColor(255, 255, 255, 180), 1))
        font = QFont("Arial", 10)
        painter.setFont(font)
        mode_text = f"Mode: {self.current_draw_mode.capitalize()}"
        painter.drawText(10, 20, mode_text)
        
        # Zoom indicator
        zoom_text = f"Zoom: {self.zoom_level:.1f}x"
        painter.drawText(10, 40, zoom_text)
    
    def get_settings(self) -> dict:
        """Get visualizer-specific settings"""
        return {
            'draw_mode': self.current_draw_mode,
            'show_grid': self.show_grid,
            'show_axes': self.show_axes,
            'persistence': self.persistence,
            'line_thickness': self.line_thickness,
            'smooth_factor': self.smooth_factor,
            'trigger_enabled': self.trigger_enabled,
            'trigger_level': self.trigger_level,
            'glow_enabled': self.glow_enabled,
            'zoom_level': self.zoom_level,
        }
    
    def apply_settings(self, settings: dict):
        """Apply visualizer-specific settings"""
        if 'draw_mode' in settings:
            self.current_draw_mode = settings['draw_mode']
        if 'show_grid' in settings:
            self.show_grid = settings['show_grid']
        if 'show_axes' in settings:
            self.show_axes = settings['show_axes']
        if 'persistence' in settings:
            self.persistence = settings['persistence']
        if 'line_thickness' in settings:
            self.line_thickness = settings['line_thickness']
        if 'smooth_factor' in settings:
            self.smooth_factor = settings['smooth_factor']
        if 'trigger_enabled' in settings:
            self.trigger_enabled = settings['trigger_enabled']
        if 'trigger_level' in settings:
            self.trigger_level = settings['trigger_level']
        if 'glow_enabled' in settings:
            self.glow_enabled = settings['glow_enabled']
        if 'zoom_level' in settings:
            self.zoom_level = settings['zoom_level']
    
    def cycle_draw_mode(self):
        """Cycle through drawing modes"""
        modes = [self.DRAW_MODE_LINES, self.DRAW_MODE_DOTS, self.DRAW_MODE_FILLED, 
                 self.DRAW_MODE_BARS, self.DRAW_MODE_MIRROR]
        current_index = modes.index(self.current_draw_mode)
        next_index = (current_index + 1) % len(modes)
        self.current_draw_mode = modes[next_index]
