"""
Settings panel widget for SnapTidy options.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QGroupBox,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SettingsPanel(QFrame):
    """Settings panel with modern design."""

    settings_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Flatten settings
        flatten_group = self.create_group_box("📁 디렉토리 평탄화")
        flatten_layout = QVBoxLayout(flatten_group)

        # Copy mode checkbox
        self.copy_mode = QCheckBox("복사 모드 (원본 유지)")
        self.copy_mode.setToolTip("파일을 이동하지 않고 복사합니다")
        self.copy_mode.setStyleSheet(
            """
            QCheckBox {
                font-size: 14px;
                color: #2c3e50;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """
        )
        flatten_layout.addWidget(self.copy_mode)

        # Output folder
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("출력 폴더:"))
        self.output_combo = QComboBox()
        self.output_combo.addItems(["flattened", "사용자 지정"])
        self.output_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """
        )
        output_layout.addWidget(self.output_combo)
        flatten_layout.addLayout(output_layout)

        layout.addWidget(flatten_group)

        # Deduplication settings
        dedup_group = self.create_group_box("🔍 중복 제거")
        dedup_layout = QVBoxLayout(dedup_group)

        # Sensitivity slider
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("민감도:"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(50)
        self.sensitivity_slider.setMaximum(100)
        self.sensitivity_slider.setValue(90)
        self.sensitivity_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """
        )
        sensitivity_layout.addWidget(self.sensitivity_slider)

        self.sensitivity_label = QLabel("90%")
        self.sensitivity_label.setStyleSheet("color: #3498db; font-weight: bold;")
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(f"{v}%")
        )
        sensitivity_layout.addWidget(self.sensitivity_label)
        dedup_layout.addLayout(sensitivity_layout)

        # Threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("스레드 수:"))
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimum(1)
        self.threads_spin.setMaximum(16)
        self.threads_spin.setValue(4)
        self.threads_spin.setStyleSheet(
            """
            QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
        """
        )
        threads_layout.addWidget(self.threads_spin)
        dedup_layout.addLayout(threads_layout)

        layout.addWidget(dedup_group)

        # Organization settings
        organize_group = self.create_group_box("📅 날짜별 정리")
        organize_layout = QVBoxLayout(organize_group)

        # Date format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("날짜 형식:"))
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["년도 (2023)", "년월 (202301)"])
        self.date_format_combo.setStyleSheet(
            """
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """
        )
        format_layout.addWidget(self.date_format_combo)
        organize_layout.addLayout(format_layout)

        layout.addWidget(organize_group)

        # Connect signals
        self.copy_mode.toggled.connect(self.emit_settings)
        self.output_combo.currentTextChanged.connect(self.emit_settings)
        self.sensitivity_slider.valueChanged.connect(self.emit_settings)
        self.threads_spin.valueChanged.connect(self.emit_settings)
        self.date_format_combo.currentTextChanged.connect(self.emit_settings)

    def create_group_box(self, title: str) -> QGroupBox:
        """Create a styled group box."""
        group = QGroupBox(title)
        group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        return group

    def setup_styles(self):
        """Setup widget styles."""
        self.setStyleSheet(
            """
            SettingsPanel {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 12px;
                margin: 10px;
            }
        """
        )

    def emit_settings(self):
        """Emit current settings."""
        settings = {
            "copy_mode": self.copy_mode.isChecked(),
            "output_folder": self.output_combo.currentText(),
            "sensitivity": self.sensitivity_slider.value() / 100.0,
            "threads": self.threads_spin.value(),
            "date_format": (
                "year" if self.date_format_combo.currentIndex() == 0 else "yearmonth"
            ),
        }
        self.settings_changed.emit(settings)

    def get_settings(self) -> dict:
        """Get current settings."""
        return {
            "copy_mode": self.copy_mode.isChecked(),
            "output_folder": self.output_combo.currentText(),
            "sensitivity": self.sensitivity_slider.value() / 100.0,
            "threads": self.threads_spin.value(),
            "date_format": (
                "year" if self.date_format_combo.currentIndex() == 0 else "yearmonth"
            ),
        }
