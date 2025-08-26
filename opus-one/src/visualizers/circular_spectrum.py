"""
Circular Spectrum Visualizer for Opus One
Frequency bars arranged in a circle with rotation effects
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath, QFont
import numpy as np
import math
from .base_visualizer import BaseVisualizer


class CircularSpectrumVisualizer(BaseVisualizer):
    """Circular frequency bar visualization with rotation effects"""
    
    def initialize(self):
        """Initialize circular spectrum specific components"""
        # Configuration
        self.num_bars = 64
        self.inner_radius_ratio = 0.3  # Inner circle radius as ratio of outer
        self.rotation_speed = 1.0  # Degrees per frame when active
        
        # Bar data
        self.bar_values = np.zeros(self.num_bars)
        self.bar_peaks = np.zeros(self.num_bars)
        self.bar_velocities = np.zeros(self.num_bars)
        
        # Animation properties
        self.rotation_angle = 0
        self.base_rotation = 0
        self.rotation_velocity = 0
        self.pulse_factor = 1.0
        
        # Physics
        self.smoothing_factor = 0.85
        self.gravity = 0.008
        self.rotation_damping = 0.95
        
        # Visual settings
        self.bar_width_angle = 360 / self.num_bars * 0.8  # Leave gaps between bars
        self.glow_enabled = True
        self.peak_indicators = True
        self.clockwise = True
        
    def get_name(self) -> str:
        return "Circular Spectrum"
    
    def get_description(self) -> str:
        return "Frequency bars arranged in a rotating circle"
    
    def process_audio_data(self):
        """Process audio data for circular visualization"""
        if not self.audio_engine:
            return
        
        # Get spectrum data
        spectrum_data = self.audio_engine.get_spectrum_data(self.num_bars)
        
        # Update bar values with smoothing
        for i in range(self.num_bars):
            target_value = spectrum_data[i]
            current_value = self.bar_values[i]
            
            # Smooth transition
            self.bar_values[i] = current_value * self.smoothing_factor + target_value * (1 - self.smoothing_factor)
            
            # Update peaks with gravity
            if self.bar_values[i] > self.bar_peaks[i]:
                self.bar_peaks[i] = self.bar_values[i]
                self.bar_velocities[i] = 0
            else:
                self.bar_velocities[i] += self.gravity
                self.bar_peaks[i] = max(self.bar_values[i], self.bar_peaks[i] - self.bar_velocities[i])
        
        # Calculate rotation based on audio energy
        try:
            rms = self.audio_engine.get_rms()
            # Add rotation velocity based on RMS
            self.rotation_velocity += rms * 5
            
            # Apply rotation
            direction = 1 if self.clockwise else -1
            self.rotation_angle += self.rotation_velocity * direction
            
            # Dampen rotation
            self.rotation_velocity *= self.rotation_damping
            
            # Keep angle in range
            self.rotation_angle = self.rotation_angle % 360
            
            # Pulse effect based on bass
            bass_energy = np.mean(spectrum_data[:8])  # First 8 bars are bass
            self.pulse_factor = 1.0 + bass_energy * 0.2
            
            # Check for beat
            if self.audio_engine.is_beat():
                self.rotation_velocity += 20  # Boost rotation on beat
                
        except:
            pass
    
    def render_visualization(self, painter: QPainter):
        """Render the circular spectrum"""
        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Calculate radii
        max_radius = min(width, height) * 0.4
        inner_radius = max_radius * self.inner_radius_ratio
        
        # Draw background gradient
        self.draw_background(painter, center_x, center_y, max_radius)
        
        # Draw center circle
        self.draw_center_circle(painter, center_x, center_y, inner_radius)
        
        # Save painter state for rotation
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle)
        
        # Draw bars
        for i in range(self.num_bars):
            angle_start = (i * 360 / self.num_bars) - (self.bar_width_angle / 2)
            
            # Calculate bar height
            bar_height = self.bar_values[i] * (max_radius - inner_radius) * self.pulse_factor
            
            # Draw the bar
            self.draw_bar(painter, i, angle_start, inner_radius, bar_height, max_radius)
            
            # Draw peak indicator if enabled
            if self.peak_indicators and self.bar_peaks[i] > 0:
                peak_height = self.bar_peaks[i] * (max_radius - inner_radius) * self.pulse_factor
                self.draw_peak(painter, angle_start, inner_radius, peak_height)
        
        painter.restore()
        
        # Draw decorative elements
        self.draw_decorations(painter, center_x, center_y, max_radius)
    
    def draw_background(self, painter: QPainter, center_x, center_y, radius):
        """Draw background with radial gradient"""
        colors = self.theme['gradients']['spectrum']
        gradient = self.create_radial_gradient(
            [QColor(20, 20, 40, 180), QColor(0, 0, 20, 220)],
            QPointF(center_x, center_y),
            radius * 2
        )
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
    
    def draw_center_circle(self, painter: QPainter, center_x, center_y, radius):
        """Draw the center circle"""
        # Outer glow
        if self.glow_enabled:
            for i in range(3):
                glow_radius = radius * (1 + i * 0.1)
                opacity = 50 - i * 15
                color = QColor(self.theme['colors']['primary'])
                color.setAlpha(opacity)
                painter.setPen(QPen(color, 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(center_x, center_y), glow_radius, glow_radius)
        
        # Main circle with gradient
        gradient = self.create_radial_gradient(
            [self.theme['colors']['primary'], self.theme['colors']['secondary']],
            QPointF(center_x, center_y),
            radius
        )
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Center text
        painter.setPen(QPen(self.theme['colors']['text'], 1))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        text_rect = QRectF(center_x - radius, center_y - 10, radius * 2, 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "OPUS")
    
    def draw_bar(self, painter: QPainter, index: int, angle_start: float, 
                  inner_radius: float, bar_height: float, max_radius: float):
        """Draw a single frequency bar"""
        if bar_height <= 0:
            return
        
        # Create path for the bar
        path = QPainterPath()
        
        # Convert to radians
        angle_start_rad = math.radians(angle_start)
        angle_end_rad = math.radians(angle_start + self.bar_width_angle)
        
        # Calculate points
        inner_start_x = inner_radius * math.cos(angle_start_rad)
        inner_start_y = inner_radius * math.sin(angle_start_rad)
        inner_end_x = inner_radius * math.cos(angle_end_rad)
        inner_end_y = inner_radius * math.sin(angle_end_rad)
        
        outer_radius = inner_radius + bar_height
        outer_start_x = outer_radius * math.cos(angle_start_rad)
        outer_start_y = outer_radius * math.sin(angle_start_rad)
        outer_end_x = outer_radius * math.cos(angle_end_rad)
        outer_end_y = outer_radius * math.sin(angle_end_rad)
        
        # Build the path
        path.moveTo(inner_start_x, inner_start_y)
        path.lineTo(outer_start_x, outer_start_y)
        path.lineTo(outer_end_x, outer_end_y)
        path.lineTo(inner_end_x, inner_end_y)
        path.closeSubpath()
        
        # Get color based on frequency range
        color = self.get_color_from_gradient(
            index / self.num_bars,
            self.theme['gradients']['spectrum']
        )
        
        # Adjust brightness based on amplitude
        intensity = self.bar_values[index]
        color.setAlpha(int(100 + 155 * intensity))
        
        # Draw the bar
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Add glow effect for high values
        if self.glow_enabled and intensity > 0.7:
            glow_color = QColor(color)
            glow_color.setAlpha(int(50 * intensity))
            painter.setBrush(QBrush(glow_color))
            
            # Slightly larger path for glow
            glow_outer_radius = outer_radius + 5
            glow_path = QPainterPath()
            glow_start_x = glow_outer_radius * math.cos(angle_start_rad)
            glow_start_y = glow_outer_radius * math.sin(angle_start_rad)
            glow_end_x = glow_outer_radius * math.cos(angle_end_rad)
            glow_end_y = glow_outer_radius * math.sin(angle_end_rad)
            
            glow_path.moveTo(outer_start_x, outer_start_y)
            glow_path.lineTo(glow_start_x, glow_start_y)
            glow_path.lineTo(glow_end_x, glow_end_y)
            glow_path.lineTo(outer_end_x, outer_end_y)
            glow_path.closeSubpath()
            
            painter.drawPath(glow_path)
    
    def draw_peak(self, painter: QPainter, angle_start: float, 
                  inner_radius: float, peak_height: float):
        """Draw peak indicator"""
        # Convert to radians
        angle_center_rad = math.radians(angle_start + self.bar_width_angle / 2)
        
        # Calculate position
        peak_radius = inner_radius + peak_height
        peak_x = peak_radius * math.cos(angle_center_rad)
        peak_y = peak_radius * math.sin(angle_center_rad)
        
        # Draw peak dot
        color = QColor(self.theme['colors']['accent'])
        color.setAlpha(200)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(peak_x, peak_y), 2, 2)
    
    def draw_decorations(self, painter: QPainter, center_x, center_y, radius):
        """Draw decorative elements"""
        # Draw rotating rings
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        for i in range(3):
            ring_radius = radius * (1.2 + i * 0.2)
            painter.drawEllipse(QPointF(center_x, center_y), ring_radius, ring_radius)
    
    def get_settings(self) -> dict:
        """Get visualizer-specific settings"""
        return {
            'num_bars': self.num_bars,
            'inner_radius_ratio': self.inner_radius_ratio,
            'rotation_speed': self.rotation_speed,
            'smoothing_factor': self.smoothing_factor,
            'glow_enabled': self.glow_enabled,
            'peak_indicators': self.peak_indicators,
            'clockwise': self.clockwise,
        }
    
    def apply_settings(self, settings: dict):
        """Apply visualizer-specific settings"""
        if 'num_bars' in settings:
            self.num_bars = settings['num_bars']
            self.bar_values = np.zeros(self.num_bars)
            self.bar_peaks = np.zeros(self.num_bars)
            self.bar_velocities = np.zeros(self.num_bars)
            self.bar_width_angle = 360 / self.num_bars * 0.8
        
        if 'inner_radius_ratio' in settings:
            self.inner_radius_ratio = settings['inner_radius_ratio']
        
        if 'rotation_speed' in settings:
            self.rotation_speed = settings['rotation_speed']
        
        if 'smoothing_factor' in settings:
            self.smoothing_factor = settings['smoothing_factor']
        
        if 'glow_enabled' in settings:
            self.glow_enabled = settings['glow_enabled']
        
        if 'peak_indicators' in settings:
            self.peak_indicators = settings['peak_indicators']
        
        if 'clockwise' in settings:
            self.clockwise = settings['clockwise']
