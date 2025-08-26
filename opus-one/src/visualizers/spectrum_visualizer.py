"""
Spectrum Visualizer for Opus One
Beautiful, smooth, animated audio spectrum visualization
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QPointF, QRectF, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient, QPainterPath
import numpy as np
import math
from typing import Optional


class SpectrumVisualizer(QWidget):
    """Beautiful spectrum visualizer with smooth animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_engine = None
        
        # Visualization settings
        self.num_bars = 64
        self.bar_values = np.zeros(self.num_bars)
        self.bar_peaks = np.zeros(self.num_bars)
        self.bar_velocities = np.zeros(self.num_bars)
        self.smoothing_factor = 0.8
        self.gravity = 0.005
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualization)
        self.fps = 60
        
        # Visual style
        self.gradient_colors = [
            QColor(138, 43, 226),   # Blue Violet
            QColor(75, 0, 130),     # Indigo
            QColor(255, 20, 147),   # Deep Pink
            QColor(255, 105, 180),  # Hot Pink
            QColor(255, 192, 203),  # Pink
        ]
        
        # Particle system for beats
        self.particles = []
        self.max_particles = 50
        
        # Background animation
        self.rotation_angle = 0
        self.pulse_factor = 1.0
        
        # Set transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
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
            # Get spectrum data
            spectrum_data = self.audio_engine.get_spectrum_data(self.num_bars)
            
            # Smooth the values
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
            
            # Check for beat and create particles
            if self.audio_engine.is_beat() and len(self.particles) < self.max_particles:
                self.create_beat_particles()
            
            # Update particles
            self.update_particles()
            
            # Update background animation
            self.rotation_angle = (self.rotation_angle + 0.5) % 360
            rms = self.audio_engine.get_rms()
            self.pulse_factor = 1.0 + rms * 0.3
        
        self.update()
    
    def create_beat_particles(self):
        """Create particles when beat is detected"""
        num_particles = np.random.randint(3, 8)
        for _ in range(num_particles):
            particle = {
                'x': self.width() / 2,
                'y': self.height() / 2,
                'vx': np.random.uniform(-5, 5),
                'vy': np.random.uniform(-8, -2),
                'size': np.random.uniform(2, 6),
                'life': 1.0,
                'color': np.random.choice(self.gradient_colors)
            }
            self.particles.append(particle)
    
    def update_particles(self):
        """Update particle positions and lifecycle"""
        gravity = 0.2
        fade_rate = 0.02
        
        particles_to_remove = []
        
        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += gravity
            
            # Update life
            particle['life'] -= fade_rate
            
            # Mark for removal if dead
            if particle['life'] <= 0:
                particles_to_remove.append(particle)
        
        # Remove dead particles
        for particle in particles_to_remove:
            self.particles.remove(particle)
    
    def paintEvent(self, event):
        """Paint the visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background effects
        self.draw_background_effects(painter)
        
        # Draw spectrum bars
        self.draw_spectrum_bars(painter)
        
        # Draw particles
        self.draw_particles(painter)
        
        # Draw center decoration
        self.draw_center_decoration(painter)
    
    def draw_background_effects(self, painter):
        """Draw animated background effects"""
        # Radial gradient background
        center = QPointF(self.width() / 2, self.height() / 2)
        gradient = QRadialGradient(center, max(self.width(), self.height()) / 2)
        gradient.setColorAt(0, QColor(20, 20, 40, 100))
        gradient.setColorAt(0.5, QColor(10, 10, 30, 150))
        gradient.setColorAt(1, QColor(0, 0, 20, 200))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
        # Draw rotating circles
        painter.save()
        painter.translate(center)
        painter.rotate(self.rotation_angle)
        
        for i in range(3):
            radius = 100 + i * 50
            opacity = 30 - i * 10
            pen = QPen(QColor(138, 43, 226, opacity))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(0, 0), radius * self.pulse_factor, radius * self.pulse_factor)
        
        painter.restore()
    
    def draw_spectrum_bars(self, painter):
        """Draw the spectrum bars with gradient"""
        if self.num_bars == 0:
            return
        
        width = self.width()
        height = self.height()
        bar_width = width / self.num_bars
        max_height = height * 0.7
        
        for i in range(self.num_bars):
            # Calculate bar dimensions
            x = i * bar_width + bar_width * 0.1
            bar_height = self.bar_values[i] * max_height
            y = height - bar_height - 50  # Leave space at bottom
            
            # Create gradient for bar
            bar_gradient = QLinearGradient(x, y + bar_height, x, y)
            
            # Color based on frequency range
            color_index = int(i / self.num_bars * len(self.gradient_colors))
            base_color = self.gradient_colors[min(color_index, len(self.gradient_colors) - 1)]
            
            # Adjust color intensity based on value
            intensity = self.bar_values[i]
            bright_color = QColor(
                min(255, base_color.red() + int(100 * intensity)),
                min(255, base_color.green() + int(100 * intensity)),
                min(255, base_color.blue() + int(100 * intensity))
            )
            
            bar_gradient.setColorAt(0, base_color)
            bar_gradient.setColorAt(1, bright_color)
            
            # Draw bar with rounded top
            painter.setBrush(QBrush(bar_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            
            bar_rect = QRectF(x, y, bar_width * 0.8, bar_height)
            painter.drawRoundedRect(bar_rect, bar_width * 0.2, bar_width * 0.2)
            
            # Draw peak indicator
            if self.bar_peaks[i] > 0:
                peak_y = height - self.bar_peaks[i] * max_height - 50
                peak_color = QColor(bright_color)
                peak_color.setAlpha(200)
                painter.setBrush(QBrush(peak_color))
                peak_rect = QRectF(x, peak_y - 3, bar_width * 0.8, 3)
                painter.drawRect(peak_rect)
            
            # Draw reflection
            reflection_height = bar_height * 0.3
            reflection_y = height - 50 + 5
            
            reflection_gradient = QLinearGradient(x, reflection_y, x, reflection_y + reflection_height)
            reflection_color = QColor(base_color)
            reflection_color.setAlpha(50)
            reflection_gradient.setColorAt(0, reflection_color)
            reflection_gradient.setColorAt(1, QColor(0, 0, 0, 0))
            
            painter.setBrush(QBrush(reflection_gradient))
            reflection_rect = QRectF(x, reflection_y, bar_width * 0.8, reflection_height)
            painter.drawRect(reflection_rect)
    
    def draw_particles(self, painter):
        """Draw particle effects"""
        for particle in self.particles:
            color = QColor(particle['color'])
            color.setAlphaF(particle['life'] * 0.8)
            
            # Draw particle with glow
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            size = particle['size'] * particle['life']
            painter.drawEllipse(QPointF(particle['x'], particle['y']), size, size)
            
            # Draw glow
            glow_color = QColor(color)
            glow_color.setAlphaF(particle['life'] * 0.2)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(QPointF(particle['x'], particle['y']), size * 2, size * 2)
    
    def draw_center_decoration(self, painter):
        """Draw decorative element in center"""
        center_x = self.width() / 2
        center_y = self.height() - 25
        
        # Draw logo/text area
        painter.setPen(QPen(QColor(255, 255, 255, 100)))
        painter.drawText(int(center_x - 50), int(center_y), 100, 20,
                        Qt.AlignmentFlag.AlignCenter, "OPUS ONE")
        
        # Draw decorative lines
        pen = QPen(QColor(138, 43, 226, 100))
        pen.setWidth(1)
        painter.setPen(pen)
        
        line_width = 100
        painter.drawLine(int(center_x - line_width), int(center_y + 10),
                        int(center_x - 20), int(center_y + 10))
        painter.drawLine(int(center_x + 20), int(center_y + 10),
                        int(center_x + line_width), int(center_y + 10))
