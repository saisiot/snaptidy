"""
Folder selector widget with drag and drop support.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QLabel,
    QVBoxLayout,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont


class FolderSelector(QFrame):
    """Modern folder selector with drag and drop support."""

    folder_selected = pyqtSignal(str)

    def __init__(
        self, title="폴더 선택", placeholder="폴더를 드래그하거나 클릭하여 선택하세요"
    ):
        super().__init__()
        self.title = title
        self.placeholder = placeholder
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Main container
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.StyledPanel)
        container.setStyleSheet(
            """
            QFrame {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                background-color: #f8f9fa;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #ecf0f1;
            }
        """
        )

        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)

        # Path input
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(self.placeholder)
        self.path_input.setReadOnly(True)
        self.path_input.setStyleSheet(
            """
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
                color: #2c3e50;
            }
        """
        )
        container_layout.addWidget(self.path_input)

        # Browse button
        self.browse_btn = QPushButton("📁")
        self.browse_btn.setToolTip("폴더 선택")
        self.browse_btn.setFixedSize(40, 40)
        self.browse_btn.clicked.connect(self.browse_folder)
        self.browse_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        container_layout.addWidget(self.browse_btn)

        layout.addWidget(container)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def setup_styles(self):
        """Setup widget styles."""
        self.setStyleSheet(
            """
            FolderSelector {
                background: transparent;
            }
        """
        )

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self, "폴더 선택", self.path_input.text() or ""
        )
        if folder:
            self.set_folder(folder)

    def set_folder(self, folder_path: str):
        """Set the selected folder path."""
        self.path_input.setText(folder_path)
        self.folder_selected.emit(folder_path)

    def get_folder(self) -> str:
        """Get the selected folder path."""
        return self.path_input.text()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            # Get the first dropped item
            path = urls[0].toLocalFile()
            # Check if it's a directory
            import os

            if os.path.isdir(path):
                self.set_folder(path)
            else:
                # If it's a file, get its directory
                self.set_folder(os.path.dirname(path))
