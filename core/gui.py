"""
SnapTidy GUI - Main application window.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QTabWidget,
    QMessageBox,
    QSplitter,
    QScrollArea,
    QFrame,
    QGroupBox,
    QCheckBox,
    QSlider,
    QComboBox,
    QLineEdit,
    QFormLayout,
    QGridLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from datetime import datetime

# Import from the original location for now
import sys

sys.path.insert(0, "gui")
from gui.widgets import FolderSelector, ProgressWidget
from . import flatten, dedup, organize


def main():
    """Main entry point for the GUI."""
    # For now, just call the original implementation
    import sys

    sys.path.insert(0, "gui")
    from gui.main import main as original_main

    original_main()
