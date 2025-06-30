"""
Progress widget with modern design and animations.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class ProgressWidget(QFrame):
    """Modern progress widget with animations."""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()
        self.is_visible = False

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Status label
        self.status_label = QLabel("준비됨")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Medium))
        self.status_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #ecf0f1;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Details label
        self.details_label = QLabel("")
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_label.setFont(QFont("Arial", 10))
        self.details_label.setStyleSheet("color: #7f8c8d;")
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)

        # Initially hidden
        self.hide()

    def setup_styles(self):
        """Setup widget styles."""
        self.setStyleSheet(
            """
            ProgressWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 12px;
                margin: 10px;
            }
        """
        )

    def show_progress(self, status: str = "작업 중..."):
        """Show the progress widget."""
        self.status_label.setText(status)
        self.progress_bar.setValue(0)
        self.show()
        self.is_visible = True

    def hide_progress(self):
        """Hide the progress widget."""
        self.hide()
        self.is_visible = False

    def update_progress(self, value: int, status: str = None, details: str = None):
        """Update progress value and status."""
        self.progress_bar.setValue(value)

        if status:
            self.status_label.setText(status)

        if details:
            self.details_label.setText(details)

    def set_status(self, status: str):
        """Set status message."""
        self.status_label.setText(status)

    def set_details(self, details: str):
        """Set details message."""
        self.details_label.setText(details)

    def animate_progress(self, target_value: int, duration: int = 1000):
        """Animate progress to target value."""
        if not self.is_visible:
            self.show_progress()

        current_value = self.progress_bar.value()
        step = (target_value - current_value) / (duration / 50)  # 50ms intervals

        def update():
            current = self.progress_bar.value()
            if abs(current - target_value) < abs(step):
                self.progress_bar.setValue(target_value)
                self.timer.stop()
            else:
                self.progress_bar.setValue(current + step)

        self.timer = QTimer()
        self.timer.timeout.connect(update)
        self.timer.start(50)
