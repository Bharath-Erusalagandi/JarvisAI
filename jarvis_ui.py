import sys
import os
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QScrollArea,
                            QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtGui import (QFont, QIcon, QMovie, QPixmap, QColor, QPalette, QLinearGradient, 
                        QBrush, QPainter, QPainterPath, QRadialGradient, QPen, QFontDatabase)

class CommunicationChannel(QObject):
    """Class to handle communication between the UI and the assistant"""
    update_signal = pyqtSignal(str, str)  # message, type (user/assistant/status)
    status_signal = pyqtSignal(str)  # status update
    
    def __init__(self):
        super().__init__()
        
    def add_message(self, message, msg_type):
        """Add a message to the chat"""
        self.update_signal.emit(message, msg_type)
        
    def update_status(self, status):
        """Update the assistant status"""
        self.status_signal.emit(status)

class GlowingCircle(QWidget):
    """Widget that creates a glowing circle animation similar to the Jarvis logo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.8
        self._inner_opacity = 0.9
        self._pulse_scale = 1.0
        self.setMinimumSize(120, 120)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Setup animations
        self.pulse_animation = QPropertyAnimation(self, b"pulseScale")
        self.pulse_animation.setDuration(2000)
        self.pulse_animation.setStartValue(0.95)
        self.pulse_animation.setEndValue(1.05)
        self.pulse_animation.setLoopCount(-1)  # Infinite loop
        self.pulse_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        self.glow_animation = QPropertyAnimation(self, b"opacity")
        self.glow_animation.setDuration(1500)
        self.glow_animation.setStartValue(0.7)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.setLoopCount(-1)  # Infinite loop
        self.glow_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Start animations
        self.pulse_animation.start()
        self.glow_animation.start()
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 174, 255, 180))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
    def paintEvent(self, event):
        """Custom paint event to draw the glowing Jarvis circle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Calculate center and sizes
        center_x = self.width() / 2
        center_y = self.height() / 2
        outer_radius = min(self.width(), self.height()) / 2 * self._pulse_scale
        inner_radius = outer_radius * 0.8
        text_radius = inner_radius * 0.7
        
        # Draw outer glow
        outer_glow = QRadialGradient(center_x, center_y, outer_radius)
        outer_glow.setColorAt(0.7, QColor(0, 174, 255, int(80 * self._opacity)))
        outer_glow.setColorAt(0.9, QColor(0, 174, 255, int(40 * self._opacity)))
        outer_glow.setColorAt(1.0, QColor(0, 174, 255, 0))
        painter.setBrush(QBrush(outer_glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRect(
            int(center_x - outer_radius),
            int(center_y - outer_radius),
            int(outer_radius * 2),
            int(outer_radius * 2)
        ))
        
        # Draw outer circle
        painter.setPen(QPen(QColor(0, 174, 255, int(255 * self._opacity)), 2))
        painter.drawEllipse(QRect(
            int(center_x - outer_radius * 0.85),
            int(center_y - outer_radius * 0.85),
            int(outer_radius * 1.7),
            int(outer_radius * 1.7)
        ))
        
        # Draw inner circle
        painter.setPen(QPen(QColor(255, 255, 255, int(220 * self._inner_opacity)), 1.5))
        painter.drawEllipse(QRect(
            int(center_x - inner_radius),
            int(center_y - inner_radius),
            int(inner_radius * 2),
            int(inner_radius * 2)
        ))
        
        # Draw "JARVIS" text
        font = QFont("Montserrat", int(text_radius * 0.4))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255, int(255 * self._inner_opacity))))
        text_rect = QRect(
            int(center_x - text_radius),
            int(center_y - text_radius),
            int(text_radius * 2),
            int(text_radius * 2)
        )
        painter.drawText(text_rect, Qt.AlignCenter, "JARVIS")
        
    def get_opacity(self):
        return self._opacity
        
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()
        
    def get_pulse_scale(self):
        return self._pulse_scale
        
    def set_pulse_scale(self, scale):
        self._pulse_scale = scale
        self.update()
        
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    pulseScale = pyqtProperty(float, get_pulse_scale, set_pulse_scale)
    
    def start_animations(self):
        """Start all animations"""
        self.pulse_animation.start()
        self.glow_animation.start()
        
    def stop_animations(self):
        """Stop all animations"""
        self.pulse_animation.stop()
        self.glow_animation.stop()

class ModernButton(QPushButton):
    """Custom button with modern styling and hover effects"""
    
    def __init__(self, text, color="#007AFF", hover_color="#0056b3", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        
        # Store colors
        self.base_color = QColor(color)
        self.hover_color = QColor(hover_color)
        self.current_color = self.base_color
        
        # Set up shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)
        
        # Set style
        self.update_style()
        
    def update_style(self):
        """Update button styling"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                color: white;
                border-radius: 24px;
                padding: 12px 24px;
                font-family: 'Montserrat', 'SF Pro Display', sans-serif;
                font-weight: 600;
                font-size: 15px;
                border: none;
            }}
        """)
        
    def enterEvent(self, event):
        """Handle mouse enter event"""
        self.current_color = self.hover_color
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 6)
        self.update_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self.current_color = self.base_color
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 4)
        self.update_style()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.LeftButton:
            self.shadow.setBlurRadius(10)
            self.shadow.setOffset(0, 2)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release event"""
        if event.button() == Qt.LeftButton:
            self.shadow.setBlurRadius(15)
            self.shadow.setOffset(0, 4)
        super().mouseReleaseEvent(event)

class JarvisUI(QMainWindow):
    """Main UI class for Jarvis"""
    
    def __init__(self, comm_channel):
        super().__init__()
        self.comm_channel = comm_channel
        self.comm_channel.update_signal.connect(self.update_chat)
        self.comm_channel.status_signal.connect(self.update_status)
        
        # Load fonts
        self.load_fonts()
        
        # Initialize UI
        self.initUI()
        
    def load_fonts(self):
        """Load custom fonts"""
        # You can add custom font files here if needed
        pass
        
    def initUI(self):
        """Initialize the UI components"""
        # Set window properties
        self.setWindowTitle('JARVIS - Voice Assistant')
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Set dark theme with glassmorphism effect
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121621;
                color: #FFFFFF;
                font-family: 'Montserrat', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(45, 45, 48, 0.5);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(85, 85, 85, 0.7);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QTextEdit {
                border-radius: 12px;
                background-color: rgba(30, 30, 40, 0.7);
                padding: 15px;
                selection-background-color: #007AFF;
                selection-color: white;
                font-size: 15px;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Header with Jarvis logo/animation
        header_layout = QHBoxLayout()
        
        # Create Jarvis circle logo
        self.jarvis_logo = GlowingCircle()
        header_layout.addWidget(self.jarvis_logo, 0, Qt.AlignLeft)
        
        # Status indicator
        self.status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Montserrat", 16, QFont.Bold))
        self.status_label.setStyleSheet("color: #4CAF50; margin-left: 15px;")
        self.status_layout.addWidget(self.status_label)
        
        # Add wake word info
        wake_word_label = QLabel("Say 'Hey Jarvis' or press Wake button")
        wake_word_label.setFont(QFont("Montserrat", 12))
        wake_word_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); margin-left: 15px;")
        self.status_layout.addWidget(wake_word_label)
        
        header_layout.addLayout(self.status_layout)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)
        
        # Add separator with gradient
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                      stop:0 rgba(0, 122, 255, 0), 
                                      stop:0.4 rgba(0, 122, 255, 180), 
                                      stop:0.6 rgba(0, 122, 255, 180), 
                                      stop:1 rgba(0, 122, 255, 0));
            min-height: 1px;
            border: none;
            margin-top: 10px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(separator)
        
        # Chat area with custom styling
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 35, 45, 0.7);
                border: 1px solid rgba(60, 60, 70, 0.5);
                border-radius: 16px;
                padding: 20px;
                color: #FFFFFF;
                font-family: 'Montserrat', 'SF Pro Display', sans-serif;
                font-size: 15px;
                line-height: 1.6;
            }
        """)
        
        # Add shadow to chat area
        chat_shadow = QGraphicsDropShadowEffect()
        chat_shadow.setBlurRadius(20)
        chat_shadow.setColor(QColor(0, 0, 0, 80))
        chat_shadow.setOffset(0, 5)
        self.chat_area.setGraphicsEffect(chat_shadow)
        
        self.chat_area.setMinimumHeight(400)
        main_layout.addWidget(self.chat_area, 1)
        
        # Control buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Wake button
        self.wake_button = ModernButton("Wake Jarvis", "#007AFF", "#0056b3")
        self.wake_button.clicked.connect(self.wake_jarvis)
        button_layout.addWidget(self.wake_button)
        
        # Stop button
        self.stop_button = ModernButton("Stop Listening", "#E74C3C", "#c0392b")
        self.stop_button.clicked.connect(self.stop_jarvis)
        button_layout.addWidget(self.stop_button)
        
        # Clear button
        self.clear_button = ModernButton("Clear Chat", "#555555", "#444444")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)
        
        # Exit button
        self.exit_button = ModernButton("Exit", "#7F8C8D", "#616A6B")
        self.exit_button.clicked.connect(self.close_application)
        button_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(button_layout)
        
        # Add welcome message
        self.update_chat("Welcome to Jarvis Voice Assistant. Press 'Wake Jarvis' to begin.", "status")
    
    def update_status(self, status):
        """Update the status label and animation"""
        if status == "listening":
            self.status_label.setText("Status: Listening...")
            self.status_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 16px; margin-left: 15px;")
            # Update logo animation
            self.jarvis_logo.start_animations()
        elif status == "processing":
            self.status_label.setText("Status: Processing...")
            self.status_label.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 16px; margin-left: 15px;")
            self.jarvis_logo.start_animations()
        elif status == "speaking":
            self.status_label.setText("Status: Speaking...")
            self.status_label.setStyleSheet("color: #9C27B0; font-weight: bold; font-size: 16px; margin-left: 15px;")
            self.jarvis_logo.start_animations()
        elif status == "idle":
            self.status_label.setText("Status: Idle")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px; margin-left: 15px;")
        elif status == "error":
            self.status_label.setText("Status: Error")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 16px; margin-left: 15px;")
    
    def update_chat(self, message, msg_type):
        """Update the chat area with new messages"""
        timestamp = time.strftime("%H:%M:%S")
        
        if msg_type == "user":
            self.chat_area.append(f'<p style="margin: 12px 0; line-height: 1.5;"><span style="color: #888888; font-size: 12px; font-family: Montserrat, sans-serif;">[{timestamp}]</span> <span style="color: #4CAF50; font-weight: bold; font-family: Montserrat, sans-serif;">You:</span> <span style="color: #FFFFFF; font-family: Montserrat, sans-serif;">{message}</span></p>')
        elif msg_type == "assistant":
            self.chat_area.append(f'<p style="margin: 12px 0; line-height: 1.5;"><span style="color: #888888; font-size: 12px; font-family: Montserrat, sans-serif;">[{timestamp}]</span> <span style="color: #007AFF; font-weight: bold; font-family: Montserrat, sans-serif;">Jarvis:</span> <span style="color: #FFFFFF; font-family: Montserrat, sans-serif;">{message}</span></p>')
        elif msg_type == "status":
            self.chat_area.append(f'<p style="margin: 12px 0; line-height: 1.5; color: rgba(255, 255, 255, 0.7); font-style: italic; font-size: 14px; font-family: Montserrat, sans-serif;"><span style="color: #888888; font-size: 12px;">[{timestamp}]</span> {message}</p>')
        elif msg_type == "error":
            self.chat_area.append(f'<p style="margin: 12px 0; line-height: 1.5; color: #F44336; font-family: Montserrat, sans-serif;"><span style="color: #888888; font-size: 12px;">[{timestamp}]</span> <span style="font-weight: bold;">Error:</span> {message}</p>')
        
        # Scroll to the bottom
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())
    
    def wake_jarvis(self):
        """Wake up Jarvis manually"""
        self.update_status("listening")
        self.comm_channel.add_message("Jarvis activated manually", "status")
    
    def stop_jarvis(self):
        """Stop Jarvis from listening"""
        self.update_status("idle")
        self.comm_channel.add_message("Stopped listening", "status")
    
    def clear_chat(self):
        """Clear the chat area"""
        self.chat_area.clear()
        self.update_chat("Chat cleared", "status")
    
    def close_application(self):
        """Close the application"""
        self.comm_channel.add_message("Shutting down Jarvis...", "status")
        QTimer.singleShot(1000, self.close)

def launch_ui():
    """Launch the Jarvis UI"""
    app = QApplication(sys.argv)
    comm_channel = CommunicationChannel()
    window = JarvisUI(comm_channel)
    window.show()
    return app, window, comm_channel

if __name__ == "__main__":
    app, window, comm = launch_ui()
    sys.exit(app.exec_())
