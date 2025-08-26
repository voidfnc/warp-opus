"""
Custom Title Bar Widget for Opus One
A solid, opaque title bar with window controls
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen


class TitleBar(QWidget):
    """Solid title bar with window controls"""
    
    minimize_signal = pyqtSignal()
    maximize_signal = pyqtSignal()
    close_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_pos = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the title bar UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e28;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 5, 0)
        layout.setSpacing(0)
        
        # Icon and title
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # App icon
        icon_label = QLabel("♪")
        icon_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 20px;
                font-weight: bold;
                padding: 0px;
            }
        """)
        title_layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel("Opus One")
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                padding: 0px;
            }
        """)
        title_layout.addWidget(name_label)
        title_layout.addStretch()
        
        layout.addWidget(title_widget, 1)
        
        # Window control buttons
        button_style = """
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
                padding: 0px;
                width: 46px;
                height: 32px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """
        
        # Minimize button
        self.minimize_btn = QPushButton("－")
        self.minimize_btn.setStyleSheet(button_style)
        self.minimize_btn.clicked.connect(self.minimize_signal.emit)
        
        # Maximize button  
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setStyleSheet(button_style)
        self.maximize_btn.clicked.connect(self.maximize_signal.emit)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setStyleSheet(button_style + """
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.close_signal.emit)
        
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
    def paintEvent(self, event):
        """Paint the solid background"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 40))
        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos and self.parent_window:
            self.parent_window.move(self.parent_window.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
