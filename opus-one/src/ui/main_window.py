"""
Main Window for Opus One Audio Visualizer
Features a modern, minimalistic design with smooth animations
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QSlider, QFileDialog, 
                            QGraphicsDropShadowEffect, QStackedWidget,
                            QFrame, QSizeGrip)
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                         QPoint, QRect, QSize, pyqtSignal, QThread,
                         QParallelAnimationGroup, pyqtProperty)
from PyQt6.QtGui import (QPalette, QColor, QPainter, QBrush, QPen,
                        QLinearGradient, QRadialGradient, QFont,
                        QFontMetrics, QIcon, QPainterPath, QRegion)
import sys
from pathlib import Path

# Import custom title bar
from .title_bar import TitleBar

# Import visualizers and audio components
from visualizers.spectrum_visualizer import SpectrumVisualizer
from visualizers.circular_spectrum import CircularSpectrumVisualizer
from visualizers.waveform_visualizer import WaveformVisualizer
try:
    from audio.simple_audio_engine import SimpleAudioEngine as AudioEngine
except ImportError:
    from audio.audio_engine import AudioEngine


class GlassFrame(QFrame):
    """Custom frame with glassmorphism effect"""
    
    def __init__(self, parent=None, solid=False):
        super().__init__(parent)
        
        if solid:
            # COMPLETELY SOLID background for title bar - NO transparency
            self.setStyleSheet("""
                QFrame {
                    background-color: rgb(30, 30, 40);
                    border: none;
                    border-radius: 0px;
                }
            """)
            # No transparency attribute for solid frames
        else:
            # Semi-transparent for other panels
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(20, 20, 30, 180);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                }
            """)
            
            # Add shadow effect only for non-solid frames
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(0)
            shadow.setColor(QColor(0, 0, 0, 100))
            self.setGraphicsEffect(shadow)


class AnimatedButton(QPushButton):
    """Custom button with hover animations"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._color = QColor(80, 80, 100)  # Initialize _color before creating animation
        self._animation = QPropertyAnimation(self, b"color")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.setStyleSheet(self._get_style())
        
    def _get_style(self):
        return f"""
            QPushButton {{
                background-color: rgba({self._color.red()}, {self._color.green()}, {self._color.blue()}, 180);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: rgba({self._color.red()+20}, {self._color.green()+20}, {self._color.blue()+20}, 200);
            }}
            QPushButton:pressed {{
                background-color: rgba({self._color.red()-20}, {self._color.green()-20}, {self._color.blue()-20}, 200);
            }}
        """
    
    def get_color(self):
        return self._color
    
    def set_color(self, color):
        self._color = color
        self.setStyleSheet(self._get_style())
    
    color = pyqtProperty(QColor, get_color, set_color)
    
    def enterEvent(self, event):
        self._animation.setStartValue(self._color)
        self._animation.setEndValue(QColor(100, 100, 120))
        self._animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._animation.setStartValue(self._color)
        self._animation.setEndValue(QColor(80, 80, 100))
        self._animation.start()
        super().leaveEvent(event)


class MainWindow(QMainWindow):
    """Main application window with modern UI"""
    
    def __init__(self):
        super().__init__()
        self.audio_engine = AudioEngine()
        self.is_playing = False
        self.current_file = None
        self.init_ui()
        self.setup_animations()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Opus One - Audio Visualizer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Make window frameless for custom design
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Central widget with gradient background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom solid title bar
        self.title_bar = TitleBar(self)
        self.title_bar.minimize_signal.connect(self.showMinimized)
        self.title_bar.maximize_signal.connect(self._toggle_maximize)
        self.title_bar.close_signal.connect(self.close)
        main_layout.addWidget(self.title_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Visualizer area
        self.visualizer_container = GlassFrame()
        visualizer_layout = QVBoxLayout(self.visualizer_container)
        visualizer_layout.setContentsMargins(10, 10, 10, 10)
        
        # Stack widget for multiple visualizers
        self.visualizer_stack = QStackedWidget()
        
        # Create all visualizers
        self.visualizers = {
            'spectrum': SpectrumVisualizer(),
            'circular': CircularSpectrumVisualizer(),
            'waveform': WaveformVisualizer(),
        }
        
        # Add visualizers to stack and store their index
        self.visualizer_indices = {}
        for name, visualizer in self.visualizers.items():
            index = self.visualizer_stack.addWidget(visualizer)
            self.visualizer_indices[name] = index
            visualizer.set_audio_engine(self.audio_engine)
        
        # Set default visualizer
        self.current_visualizer_name = 'spectrum'
        self.current_visualizer = self.visualizers[self.current_visualizer_name]
        self.visualizer_stack.setCurrentIndex(self.visualizer_indices[self.current_visualizer_name])
        
        visualizer_layout.addWidget(self.visualizer_stack)
        
        content_layout.addWidget(self.visualizer_container, 1)
        
        # Control panel
        self.control_panel = self.create_control_panel()
        content_layout.addWidget(self.control_panel)
        
        main_layout.addWidget(content_widget)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def _toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def create_control_panel(self):
        """Create audio control panel"""
        panel = GlassFrame()
        panel.setFixedHeight(100)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # File selection button
        self.file_btn = AnimatedButton("📁 Open File")
        self.file_btn.clicked.connect(self.open_file)
        layout.addWidget(self.file_btn)
        
        # Play/Pause button
        self.play_btn = AnimatedButton("▶")
        self.play_btn.setFixedSize(60, 60)
        self.play_btn.setStyleSheet(self.play_btn.styleSheet() + """
            QPushButton {
                font-size: 24px;
                border-radius: 30px;
            }
        """)
        self.play_btn.clicked.connect(self.toggle_playback)
        layout.addWidget(self.play_btn)
        
        # Seek slider
        seek_container = QWidget()
        seek_layout = QVBoxLayout(seek_container)
        seek_layout.setContentsMargins(0, 0, 0, 0)
        seek_layout.setSpacing(5)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 12px;")
        seek_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: rgba(255, 255, 255, 0.1);
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b, stop:1 #ee5a24);
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:1 #ee5a24);
                border-radius: 3px;
            }
        """)
        seek_layout.addWidget(self.seek_slider)
        
        layout.addWidget(seek_container, 1)
        
        # Volume control
        volume_container = QWidget()
        volume_layout = QVBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(5)
        
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("color: white; font-size: 18px;")
        volume_layout.addWidget(volume_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet(self.seek_slider.styleSheet())
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(self.volume_slider)
        
        layout.addWidget(volume_container)
        
        # Visualization selector buttons
        viz_buttons_widget = QWidget()
        viz_buttons_layout = QVBoxLayout(viz_buttons_widget)
        viz_buttons_layout.setContentsMargins(0, 0, 0, 0)
        viz_buttons_layout.setSpacing(5)
        
        viz_label = QLabel("Visualizer")
        viz_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 10px;")
        viz_buttons_layout.addWidget(viz_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        viz_selector_widget = QWidget()
        viz_selector_layout = QHBoxLayout(viz_selector_widget)
        viz_selector_layout.setContentsMargins(0, 0, 0, 0)
        viz_selector_layout.setSpacing(5)
        
        # Previous visualizer button
        self.prev_viz_btn = AnimatedButton("◀")
        self.prev_viz_btn.setFixedSize(30, 30)
        self.prev_viz_btn.clicked.connect(self.previous_visualizer)
        viz_selector_layout.addWidget(self.prev_viz_btn)
        
        # Current visualizer name
        self.viz_name_label = QLabel("Spectrum")
        self.viz_name_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        self.viz_name_label.setFixedWidth(80)
        self.viz_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        viz_selector_layout.addWidget(self.viz_name_label)
        
        # Next visualizer button
        self.next_viz_btn = AnimatedButton("▶")
        self.next_viz_btn.setFixedSize(30, 30)
        self.next_viz_btn.clicked.connect(self.next_visualizer)
        viz_selector_layout.addWidget(self.next_viz_btn)
        
        viz_buttons_layout.addWidget(viz_selector_widget)
        layout.addWidget(viz_buttons_widget)
        
        return panel
    
    def apply_dark_theme(self):
        """Apply dark theme with gradients"""
        self.setStyleSheet("""
            #contentWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
            }
        """)
    
    def setup_animations(self):
        """Setup UI animations"""
        # Fade in animation for visualizer
        self.fade_animation = QPropertyAnimation(self.visualizer_container, b"windowOpacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
    
    def setup_timers(self):
        """Setup timers for UI updates"""
        # Timer for updating time display
        self.time_update_timer = QTimer()
        self.time_update_timer.timeout.connect(self.update_time_display)
        self.time_update_timer.start(100)  # Update every 100ms
        
        # Flag to prevent slider feedback loop
        self.user_seeking = False
        
        # Connect seek slider signals
        self.seek_slider.sliderPressed.connect(self.on_seek_start)
        self.seek_slider.sliderReleased.connect(self.on_seek_end)
        self.seek_slider.valueChanged.connect(self.on_seek_change)
    
    def update_time_display(self):
        """Update time label and seek slider"""
        if self.audio_engine and self.current_file:
            current_time = self.audio_engine.get_current_time()
            total_time = self.audio_engine.get_total_time()
            
            # Format time as MM:SS
            current_mins = int(current_time // 60)
            current_secs = int(current_time % 60)
            total_mins = int(total_time // 60)
            total_secs = int(total_time % 60)
            
            time_text = f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}"
            self.time_label.setText(time_text)
            
            # Update seek slider position (only if user is not dragging)
            if not self.user_seeking and total_time > 0:
                slider_position = int((current_time / total_time) * 1000)
                self.seek_slider.setMaximum(1000)
                self.seek_slider.setValue(slider_position)
            
            # Check if playback finished
            if self.is_playing and current_time >= total_time - 0.1:
                self.is_playing = False
                self.play_btn.setText("▶")
                self.current_visualizer.stop_visualization()
    
    def on_seek_start(self):
        """Called when user starts dragging seek slider"""
        self.user_seeking = True
    
    def on_seek_end(self):
        """Called when user releases seek slider"""
        self.user_seeking = False
        # Perform the actual seek
        if self.audio_engine and self.current_file:
            total_time = self.audio_engine.get_total_time()
            if total_time > 0:
                seek_position = self.seek_slider.value() / 1000.0
                self.audio_engine.seek(seek_position)
    
    def on_seek_change(self, value):
        """Update time display while seeking"""
        if self.user_seeking and self.audio_engine and self.current_file:
            total_time = self.audio_engine.get_total_time()
            if total_time > 0:
                current_time = (value / 1000.0) * total_time
                current_mins = int(current_time // 60)
                current_secs = int(current_time % 60)
                total_mins = int(total_time // 60)
                total_secs = int(total_time % 60)
                
                time_text = f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}"
                self.time_label.setText(time_text)
        
    def toggle_maximize(self):
        """Toggle between maximized and normal window"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def open_file(self):
        """Open audio file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg);;All Files (*.*)"
        )
        
        if file_path:
            try:
                self.current_file = file_path
                success = self.audio_engine.load_file(file_path)
                if success:
                    # Update all visualizers with new audio engine
                    for visualizer in self.visualizers.values():
                        visualizer.set_audio_engine(self.audio_engine)
                    self.file_btn.setText(f"📁 {Path(file_path).name}")
                else:
                    self.file_btn.setText("📁 Failed to load")
                    self.current_file = None
            except Exception as e:
                print(f"Error loading file: {e}")
                self.file_btn.setText("📁 Error loading")
                self.current_file = None
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.current_file:
            if self.is_playing:
                self.audio_engine.pause()
                self.play_btn.setText("▶")
            else:
                self.audio_engine.play()
                self.play_btn.setText("⏸")
                self.current_visualizer.start_visualization()
            self.is_playing = not self.is_playing
    
    def change_volume(self, value):
        """Change audio volume"""
        self.audio_engine.set_volume(value / 100)
    
    def show_viz_options(self):
        """Show visualization options"""
        # This will be implemented with a popup menu
        pass
    
    def switch_visualizer(self, name):
        """Switch to a different visualizer"""
        if name in self.visualizers:
            # Stop current visualizer
            if self.is_playing:
                self.current_visualizer.stop_visualization()
            
            # Switch to new visualizer
            self.current_visualizer_name = name
            self.current_visualizer = self.visualizers[name]
            self.visualizer_stack.setCurrentIndex(self.visualizer_indices[name])
            
            # Update label
            display_names = {
                'spectrum': 'Spectrum',
                'circular': 'Circular',
                'waveform': 'Waveform'
            }
            self.viz_name_label.setText(display_names.get(name, name.capitalize()))
            
            # Start new visualizer if playing
            if self.is_playing:
                self.current_visualizer.start_visualization()
    
    def next_visualizer(self):
        """Switch to next visualizer"""
        names = list(self.visualizers.keys())
        current_index = names.index(self.current_visualizer_name)
        next_index = (current_index + 1) % len(names)
        self.switch_visualizer(names[next_index])
    
    def previous_visualizer(self):
        """Switch to previous visualizer"""
        names = list(self.visualizers.keys())
        current_index = names.index(self.current_visualizer_name)
        prev_index = (current_index - 1) % len(names)
        self.switch_visualizer(names[prev_index])
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop event for audio files"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
                self.current_file = file_path
                self.audio_engine.load_file(file_path)
                # Update all visualizers
                for visualizer in self.visualizers.values():
                    visualizer.set_audio_engine(self.audio_engine)
                self.file_btn.setText(f"📁 {Path(file_path).name}")
                break
    
    def paintEvent(self, event):
        """Custom paint event for rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # Set clip region
        painter.setClipPath(path)
        
        # Paint background
        super().paintEvent(event)
