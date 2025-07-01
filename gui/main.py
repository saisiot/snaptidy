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

from .widgets import FolderSelector, ProgressWidget
from snaptidy import flatten, dedup, organize


class WorkerThread(QThread):
    """Background worker thread for SnapTidy operations."""

    progress_updated = pyqtSignal(int, str, str)
    operation_completed = pyqtSignal(bool, str)

    def __init__(self, operation, path, settings):
        super().__init__()
        self.operation = operation
        self.path = path
        self.settings = settings

    def run(self):
        """Run the operation in background thread."""
        try:
            if self.operation == "flatten":
                self.run_flatten()
            elif self.operation == "dedup":
                self.run_dedup()
            elif self.operation == "organize":
                self.run_organize()
        except Exception as e:
            self.operation_completed.emit(False, str(e))

    def run_flatten(self):
        """Run flatten operation."""
        self.progress_updated.emit(10, "디렉토리 스캔 중...", "")

        # Get settings
        copy_mode = self.settings.get("copy_mode", False)
        output_folder = self.settings.get("output_folder", "flattened")
        enable_logging = self.settings.get("enable_logging", False)

        self.progress_updated.emit(30, "파일 처리 중...", "")

        # Run flatten operation
        flatten.run(
            path=self.path,
            copy=copy_mode,
            output=None if output_folder == "flattened" else output_folder,
            enable_logging=enable_logging,
        )

        self.progress_updated.emit(100, "완료!", "디렉토리 평탄화가 완료되었습니다.")
        self.operation_completed.emit(
            True, "디렉토리 평탄화가 성공적으로 완료되었습니다."
        )

    def run_dedup(self):
        """Run deduplication operation."""
        self.progress_updated.emit(10, "파일 스캔 중...", "")

        sensitivity = self.settings.get("sensitivity", 0.9)
        threads = self.settings.get("threads", 4)
        move_to_folder = self.settings.get("move_to_folder", None)

        self.progress_updated.emit(30, "중복 파일 검색 중...", "")

        # Run dedup operation
        dedup.run(
            path=self.path,
            sensitivity=sensitivity,
            threads=threads,
            move_to_folder=move_to_folder,
        )

        self.progress_updated.emit(100, "완료!", "중복 제거가 완료되었습니다.")
        self.operation_completed.emit(True, "중복 제거가 성공적으로 완료되었습니다.")

    def run_organize(self):
        """Run organization operation."""
        self.progress_updated.emit(10, "파일 분석 중...", "")

        date_format = self.settings.get("date_format", "year")
        unclassified_mode = self.settings.get("unclassified_mode", False)

        self.progress_updated.emit(30, "날짜별 정리 중...", "")

        # Run organize operation
        organize.run(
            path=self.path, date_format=date_format, unclassified_mode=unclassified_mode
        )

        self.progress_updated.emit(100, "완료!", "날짜별 정리가 완료되었습니다.")
        self.operation_completed.emit(True, "날짜별 정리가 성공적으로 완료되었습니다.")


class AllOperationsThread(QThread):
    """Background worker thread for running all operations sequentially."""

    progress_updated = pyqtSignal(int, str, str)
    operation_completed = pyqtSignal(bool, str)

    def __init__(self, path, flatten_settings, dedup_settings, organize_settings):
        super().__init__()
        self.path = path
        self.flatten_settings = flatten_settings
        self.dedup_settings = dedup_settings
        self.organize_settings = organize_settings

    def run(self):
        """Run all operations sequentially."""
        try:
            total_operations = 3
            current_operation = 0

            # Step 1: Flatten
            self.progress_updated.emit(
                int(current_operation * 100 / total_operations),
                "1/3 디렉토리 평탄화 시작...",
                "",
            )

            copy_mode = self.flatten_settings.get("copy_mode", False)
            output_folder = self.flatten_settings.get("output_folder", "flattened")

            flatten.run(
                path=self.path,
                copy=copy_mode,
                output=None if output_folder == "flattened" else output_folder,
            )

            current_operation += 1
            self.progress_updated.emit(
                int(current_operation * 100 / total_operations),
                "2/3 중복 제거 시작...",
                "디렉토리 평탄화 완료",
            )

            # Step 2: Dedup
            sensitivity = self.dedup_settings.get("sensitivity", 0.9)
            threads = self.dedup_settings.get("threads", 4)
            move_to_folder = self.dedup_settings.get("move_to_folder", None)

            dedup.run(
                path=self.path,
                sensitivity=sensitivity,
                threads=threads,
                move_to_folder=move_to_folder,
            )

            current_operation += 1
            self.progress_updated.emit(
                int(current_operation * 100 / total_operations),
                "3/3 날짜별 정리 시작...",
                "중복 제거 완료",
            )

            # Step 3: Organize
            date_format = self.organize_settings.get("date_format", "year")
            unclassified_mode = self.organize_settings.get("unclassified_mode", False)

            organize.run(
                path=self.path,
                date_format=date_format,
                unclassified_mode=unclassified_mode,
            )

            self.progress_updated.emit(
                100, "모든 작업 완료!", "전체 정리 작업이 성공적으로 완료되었습니다."
            )
            self.operation_completed.emit(
                True, "모든 작업이 성공적으로 완료되었습니다!"
            )

        except Exception as e:
            self.operation_completed.emit(False, str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.all_operations_thread = None
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("SnapTidy - 사진 라이브러리 정리 도구")
        self.setMinimumSize(1200, 900)
        self.resize(1400, 1000)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
        """
        )

        # Content widget for scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # Header
        header = self.create_header()
        content_layout.addWidget(header)

        # Folder selector
        self.folder_selector = FolderSelector("📁 대상 폴더")
        self.folder_selector.folder_selected.connect(self.on_folder_selected)
        content_layout.addWidget(self.folder_selector)

        # Logging section
        logging_section = self.create_logging_section()
        content_layout.addWidget(logging_section)

        # Operations grid
        operations_widget = self.create_operations_grid()
        content_layout.addWidget(operations_widget)

        # Run All button with warning
        run_all_section = self.create_run_all_section()
        content_layout.addWidget(run_all_section)

        # Recovery section
        recovery_section = self.create_recovery_section()
        content_layout.addWidget(recovery_section)

        # Progress widget
        self.progress_widget = ProgressWidget()
        content_layout.addWidget(self.progress_widget)

        # Results area
        results_group = QFrame()
        results_group.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 12px;
                margin: 10px;
            }
        """
        )

        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(20, 20, 20, 20)

        results_title = QLabel("📊 작업 결과")
        results_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        results_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        results_layout.addWidget(results_title)

        self.results_label = QLabel("폴더를 선택하고 작업을 시작하세요.")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        results_layout.addWidget(self.results_label)

        content_layout.addWidget(results_group)

        # Set the content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_header(self) -> QWidget:
        """Create the header section."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Logo and title
        title_layout = QVBoxLayout()

        title = QLabel("SnapTidy")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(title)

        subtitle = QLabel("사진 라이브러리 정리 도구")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #7f8c8d;")
        title_layout.addWidget(subtitle)

        layout.addLayout(title_layout)
        layout.addStretch()

        # Version info
        version_label = QLabel("v0.1.0")
        version_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(version_label)

        return header

    def create_logging_section(self) -> QWidget:
        """Create the logging options section."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Logging checkbox
        self.logging_checkbox = QCheckBox("📋 작업 로그 기록 (복구 가능)")
        self.logging_checkbox.setStyleSheet(
            """
            QCheckBox {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
            }
        """
        )
        self.logging_checkbox.setToolTip(
            "체크하면 모든 작업을 CSV 파일로 기록하고 복구 스크립트를 생성합니다. 이 옵션을 사용하면 파일이 삭제되지 않고 이동만 됩니다."
        )
        layout.addWidget(self.logging_checkbox)

        # Logging info
        logging_info = QLabel("⚠️ 로그 모드에서는 파일 삭제가 비활성화됩니다")
        logging_info.setStyleSheet(
            """
            color: #e67e22;
            font-size: 11px;
            font-weight: bold;
        """
        )
        layout.addWidget(logging_info)

        layout.addStretch()
        return widget

    def create_operations_grid(self) -> QWidget:
        """Create the operations grid with all options."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(20)

        # Flatten section
        flatten_group = self.create_flatten_section()
        layout.addWidget(flatten_group, 0, 0)

        # Dedup section
        dedup_group = self.create_dedup_section()
        layout.addWidget(dedup_group, 0, 1)

        # Organize section
        organize_group = self.create_organize_section()
        layout.addWidget(organize_group, 0, 2)

        return widget

    def create_flatten_section(self) -> QGroupBox:
        """Create the flatten operation section."""
        group = QGroupBox("📁 디렉토리 평탄화")
        group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """
        )

        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Description
        desc_label = QLabel("모든 하위 디렉토리의 파일을 하나의 폴더로 평탄화합니다.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "color: #2c3e50; font-size: 12px; font-weight: normal;"
        )
        layout.addWidget(desc_label)

        # Options
        options_layout = QFormLayout()
        options_layout.setSpacing(10)

        # Copy mode option
        self.copy_checkbox = QCheckBox("파일 복사 모드 (이동 대신)")
        self.copy_checkbox.setStyleSheet("font-size: 12px; font-weight: normal;")
        options_layout.addRow("", self.copy_checkbox)

        # Output folder option
        self.output_edit = QLineEdit("flattened")
        self.output_edit.setPlaceholderText("출력 폴더명")
        self.output_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """
        )
        options_layout.addRow("출력 폴더:", self.output_edit)

        layout.addLayout(options_layout)

        # Execute button
        self.flatten_btn = QPushButton("📁 평탄화 실행")
        self.flatten_btn.setFixedHeight(40)
        self.flatten_btn.clicked.connect(lambda: self.start_operation("flatten"))
        self.flatten_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        layout.addWidget(self.flatten_btn)

        return group

    def create_dedup_section(self) -> QGroupBox:
        """Create the deduplication operation section."""
        group = QGroupBox("🔍 중복 제거")
        group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e74c3c;
            }
        """
        )

        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Description
        desc_label = QLabel(
            "중복 파일을 찾아서 제거합니다. 정확한 중복과 유사한 이미지 모두 감지합니다."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "color: #2c3e50; font-size: 12px; font-weight: normal;"
        )
        layout.addWidget(desc_label)

        # Options
        options_layout = QFormLayout()
        options_layout.setSpacing(10)

        # Sensitivity slider
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(0)
        self.sensitivity_slider.setMaximum(100)
        self.sensitivity_slider.setValue(90)
        self.sensitivity_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #e74c3c;
                border: 1px solid #c0392b;
                width: 16px;
                margin: -2px 0;
                border-radius: 8px;
            }
        """
        )

        self.sensitivity_label = QLabel("0.9")
        self.sensitivity_label.setStyleSheet(
            "font-size: 12px; color: #2c3e50; font-weight: normal;"
        )
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)

        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(self.sensitivity_slider)
        sensitivity_layout.addWidget(self.sensitivity_label)
        options_layout.addRow("유사도:", sensitivity_layout)

        # Threads combo
        self.threads_combo = QComboBox()
        self.threads_combo.addItems(["1", "2", "4", "8", "16"])
        self.threads_combo.setCurrentText("4")
        self.threads_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """
        )
        options_layout.addRow("스레드:", self.threads_combo)

        # Duplicate handling option
        self.move_duplicates_checkbox = QCheckBox("중복 파일을 폴더로 이동 (삭제 대신)")
        self.move_duplicates_checkbox.setStyleSheet(
            "font-size: 12px; font-weight: normal;"
        )
        self.move_duplicates_checkbox.setToolTip(
            "체크하면 중복 파일을 삭제하지 않고 'duplicates' 폴더로 이동합니다."
        )
        options_layout.addRow("", self.move_duplicates_checkbox)

        # Connect logging checkbox to control duplicate handling
        self.logging_checkbox.stateChanged.connect(self.on_logging_changed)

        # Duplicate folder option
        self.duplicate_folder_edit = QLineEdit("duplicates")
        self.duplicate_folder_edit.setPlaceholderText("중복 파일 폴더명")
        self.duplicate_folder_edit.setStyleSheet(
            """
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """
        )
        options_layout.addRow("중복 폴더:", self.duplicate_folder_edit)

        layout.addLayout(options_layout)

        # Execute button
        self.dedup_btn = QPushButton("🔍 중복 제거 실행")
        self.dedup_btn.setFixedHeight(40)
        self.dedup_btn.clicked.connect(lambda: self.start_operation("dedup"))
        self.dedup_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        layout.addWidget(self.dedup_btn)

        return group

    def create_organize_section(self) -> QGroupBox:
        """Create the organization operation section."""
        group = QGroupBox("📅 날짜별 정리")
        group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #27ae60;
            }
        """
        )

        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Description
        desc_label = QLabel(
            "파일을 촬영 날짜별로 자동 정리합니다. EXIF 데이터를 기반으로 년도 또는 년도+월별로 폴더를 생성합니다."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "color: #2c3e50; font-size: 12px; font-weight: normal;"
        )
        layout.addWidget(desc_label)

        # Options
        options_layout = QFormLayout()
        options_layout.setSpacing(10)

        # Date format combo
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["year (년도별)", "yearmonth (년도+월별)"])
        self.date_format_combo.setCurrentText("year (년도별)")
        self.date_format_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """
        )
        options_layout.addRow("날짜 형식:", self.date_format_combo)

        # Unclassified files option
        self.unclassified_checkbox = QCheckBox("미분류 파일을 별도 폴더에 보관")
        self.unclassified_checkbox.setStyleSheet(
            "font-size: 12px; font-weight: normal;"
        )
        self.unclassified_checkbox.setToolTip(
            "체크하면 날짜 정보가 없는 파일들을 'unclassified' 폴더에 보관합니다."
        )
        options_layout.addRow("", self.unclassified_checkbox)

        layout.addLayout(options_layout)

        # Execute button
        self.organize_btn = QPushButton("📅 정리 실행")
        self.organize_btn.setFixedHeight(40)
        self.organize_btn.clicked.connect(lambda: self.start_operation("organize"))
        self.organize_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        layout.addWidget(self.organize_btn)

        return group

    def create_run_all_section(self) -> QWidget:
        """Create the run all operations section with warning."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Run All button
        self.run_all_btn = QPushButton("🚀 모든 작업 순차 실행")
        self.run_all_btn.setFixedHeight(50)
        self.run_all_btn.clicked.connect(self.start_all_operations)
        self.run_all_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        layout.addWidget(self.run_all_btn)

        # Warning message
        warning_label = QLabel(
            "⚠️  경고: 모든 작업이 순차적으로 실행됩니다 (평탄화 → 중복제거 → 날짜별정리). 실행 전에 백업을 권장합니다!"
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet(
            """
            color: #e67e22;
            font-size: 12px;
            font-weight: bold;
            background-color: #fdf2e9;
            border: 1px solid #f39c12;
            border-radius: 6px;
            padding: 10px;
        """
        )
        layout.addWidget(warning_label)

        return widget

    def create_recovery_section(self) -> QWidget:
        """Create the recovery section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Recovery button
        self.recovery_btn = QPushButton("🔄 복구")
        self.recovery_btn.setFixedHeight(50)
        self.recovery_btn.clicked.connect(self.generate_recovery_script)
        self.recovery_btn.setEnabled(False)  # Initially disabled
        self.recovery_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        layout.addWidget(self.recovery_btn)

        # Recovery info label
        self.recovery_info = QLabel("📋 로그 파일이 있을 때만 복구가 가능합니다.")
        self.recovery_info.setStyleSheet(
            "color: #7f8c8d; font-size: 11px; margin-top: 5px;"
        )
        self.recovery_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.recovery_info)

        return widget

    def update_sensitivity_label(self, value):
        """Update sensitivity label when slider changes."""
        self.sensitivity_label.setText(f"{value / 100:.1f}")

    def setup_styles(self):
        """Setup window styles."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f8f9fa;
            }
        """
        )

    def on_folder_selected(self, folder_path: str):
        """Handle folder selection."""
        if folder_path and os.path.exists(folder_path):
            self.enable_all_buttons()
            self.check_recovery_availability(folder_path)
        else:
            self.disable_all_buttons()

    def check_recovery_availability(self, folder_path: str):
        """Check if recovery is available based on log files."""
        log_files = []
        for log_name in [
            "snaptidy_flatten_log.csv",
            "snaptidy_dedup_log.csv",
            "snaptidy_organize_log.csv",
        ]:
            log_path = os.path.join(folder_path, log_name)
            if os.path.exists(log_path):
                log_files.append(log_name)

        if log_files:
            self.recovery_btn.setEnabled(True)
            self.recovery_info.setText(
                f"📋 복구 가능: {len(log_files)}개 로그 파일 발견"
            )
            self.recovery_info.setStyleSheet(
                "color: #27ae60; font-size: 11px; margin-top: 5px;"
            )
        else:
            self.recovery_btn.setEnabled(False)
            self.recovery_info.setText("📋 로그 파일이 있을 때만 복구가 가능합니다.")
            self.recovery_info.setStyleSheet(
                "color: #7f8c8d; font-size: 11px; margin-top: 5px;"
            )

    def on_logging_changed(self, state):
        """Handle logging checkbox state change."""
        if state == Qt.CheckState.Checked:
            # When logging is enabled, force move mode for duplicates
            self.move_duplicates_checkbox.setChecked(True)
            self.move_duplicates_checkbox.setEnabled(False)
            self.results_label.setText(
                "📋 로그 모드 활성화: 모든 작업이 기록되고 파일 삭제가 비활성화됩니다."
            )
        else:
            # When logging is disabled, allow user to choose duplicate handling
            self.move_duplicates_checkbox.setEnabled(True)
            self.results_label.setText("폴더를 선택하고 작업을 시작하세요.")

    def start_operation(self, operation: str):
        """Start a single SnapTidy operation."""
        folder_path = self.folder_selector.get_folder()
        if not folder_path:
            QMessageBox.warning(self, "경고", "폴더를 선택해주세요.")
            return

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "경고", "선택한 폴더가 존재하지 않습니다.")
            return

        # Get logging setting
        enable_logging = self.logging_checkbox.isChecked()

        # Get settings for the specific operation
        if operation == "flatten":
            settings = {
                "copy_mode": self.copy_checkbox.isChecked(),
                "output_folder": self.output_edit.text().strip() or "flattened",
                "enable_logging": enable_logging,
            }
        elif operation == "dedup":
            settings = {
                "sensitivity": self.sensitivity_slider.value() / 100,
                "threads": int(self.threads_combo.currentText()),
                "move_to_folder": (
                    self.duplicate_folder_edit.text().strip()
                    if self.move_duplicates_checkbox.isChecked()
                    else None
                ),
                "enable_logging": enable_logging,
            }
        elif operation == "organize":
            date_format = self.date_format_combo.currentText()
            settings = {
                "date_format": "yearmonth" if "yearmonth" in date_format else "year",
                "unclassified_mode": self.unclassified_checkbox.isChecked(),
                "enable_logging": enable_logging,
            }

        # Disable all buttons during operation
        self.disable_all_buttons()

        # Start worker thread
        self.worker_thread = WorkerThread(operation, folder_path, settings)
        self.worker_thread.progress_updated.connect(
            self.progress_widget.update_progress
        )
        self.worker_thread.operation_completed.connect(self.on_operation_completed)
        self.worker_thread.start()

        # Show progress
        operation_names = {
            "flatten": "디렉토리 평탄화",
            "dedup": "중복 제거",
            "organize": "날짜별 정리",
        }
        self.progress_widget.show_progress(f"{operation_names[operation]} 시작...")

    def start_all_operations(self):
        """Start all operations sequentially."""
        folder_path = self.folder_selector.get_folder()
        if not folder_path:
            QMessageBox.warning(self, "경고", "폴더를 선택해주세요.")
            return

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "경고", "선택한 폴더가 존재하지 않습니다.")
            return

        # Confirm with user
        reply = QMessageBox.question(
            self,
            "확인",
            "모든 작업을 순차적으로 실행하시겠습니까?\n\n1. 디렉토리 평탄화\n2. 중복 제거\n3. 날짜별 정리\n\n⚠️ 백업을 권장합니다!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Get settings for all operations
        flatten_settings = {
            "copy_mode": self.copy_checkbox.isChecked(),
            "output_folder": self.output_edit.text().strip() or "flattened",
        }

        dedup_settings = {
            "sensitivity": self.sensitivity_slider.value() / 100,
            "threads": int(self.threads_combo.currentText()),
            "move_to_folder": (
                self.duplicate_folder_edit.text().strip()
                if self.move_duplicates_checkbox.isChecked()
                else None
            ),
        }

        date_format = self.date_format_combo.currentText()
        organize_settings = {
            "date_format": "yearmonth" if "yearmonth" in date_format else "year",
            "unclassified_mode": self.unclassified_checkbox.isChecked(),
        }

        # Disable all buttons during operation
        self.disable_all_buttons()

        # Start all operations thread
        self.all_operations_thread = AllOperationsThread(
            folder_path, flatten_settings, dedup_settings, organize_settings
        )
        self.all_operations_thread.progress_updated.connect(
            self.progress_widget.update_progress
        )
        self.all_operations_thread.operation_completed.connect(
            self.on_operation_completed
        )
        self.all_operations_thread.start()

        # Show progress
        self.progress_widget.show_progress("모든 작업 시작...")

    def disable_all_buttons(self):
        """Disable all operation buttons."""
        self.flatten_btn.setEnabled(False)
        self.dedup_btn.setEnabled(False)
        self.organize_btn.setEnabled(False)
        self.run_all_btn.setEnabled(False)
        self.recovery_btn.setEnabled(False)

    def enable_all_buttons(self):
        """Enable all operation buttons."""
        self.flatten_btn.setEnabled(True)
        self.dedup_btn.setEnabled(True)
        self.organize_btn.setEnabled(True)
        self.run_all_btn.setEnabled(True)
        self.recovery_btn.setEnabled(True)

    def on_operation_completed(self, success: bool, message: str):
        """Handle operation completion."""
        self.enable_all_buttons()

        # Update results
        if success:
            self.results_label.setText(f"✅ {message}")
            self.results_label.setStyleSheet("color: #27ae60; font-size: 12px;")
        else:
            self.results_label.setText(f"❌ {message}")
            self.results_label.setStyleSheet("color: #e74c3c; font-size: 12px;")

        # Check recovery availability after operation
        folder_path = self.folder_selector.get_folder()
        if folder_path:
            self.check_recovery_availability(folder_path)

    def generate_recovery_script(self):
        """Generate a recovery script for the selected operations."""
        folder_path = self.folder_selector.get_folder()
        if not folder_path:
            QMessageBox.warning(self, "경고", "폴더를 선택해주세요.")
            return

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "경고", "선택한 폴더가 존재하지 않습니다.")
            return

        # Check if log files exist
        log_files = []
        for log_name in [
            "snaptidy_flatten_log.csv",
            "snaptidy_dedup_log.csv",
            "snaptidy_organize_log.csv",
        ]:
            log_path = os.path.join(folder_path, log_name)
            if os.path.exists(log_path):
                log_files.append((log_name, log_path))

        if not log_files:
            QMessageBox.information(
                self,
                "정보",
                "복구할 작업 로그가 없습니다. 먼저 로그 모드로 작업을 실행해주세요.",
            )
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "복구 확인",
            f"총 {len(log_files)}개 로그 파일에서 복구를 진행하시겠습니까?\n\n"
            "이 작업은 SnapTidy로 수행된 작업들을 되돌립니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Generate recovery script
        try:
            recovery_script_path = os.path.join(folder_path, "snaptidy_recovery.py")

            # Combine all log files and generate recovery script
            all_operations = []
            for log_name, log_path in log_files:
                with open(log_path, "r", encoding="utf-8") as f:
                    import csv

                    reader = csv.DictReader(f)
                    for row in reader:
                        all_operations.append(row)

            if not all_operations:
                QMessageBox.information(
                    self, "정보", "로그 파일에 복구할 작업이 없습니다."
                )
                return

            # Generate recovery script content
            script_content = self.generate_recovery_script_content(all_operations)

            with open(recovery_script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            # Make the script executable
            os.chmod(recovery_script_path, 0o755)

            # Show success message with execution instructions
            QMessageBox.information(
                self,
                "복구 스크립트 생성 완료",
                f"복구 스크립트가 생성되었습니다:\n\n{recovery_script_path}\n\n"
                f"터미널에서 다음 명령어로 복구를 실행하세요:\n\n"
                f"cd '{folder_path}'\n"
                f"python snaptidy_recovery.py\n\n"
                f"⚠️ 복구 전에 중요한 파일들을 백업하시기 바랍니다.",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "오류", f"복구 스크립트 생성 중 오류가 발생했습니다:\n{str(e)}"
            )

    def generate_recovery_script_content(self, operations):
        """Generate recovery script content from operations."""
        script_lines = [
            "#!/usr/bin/env python3",
            "# SnapTidy Recovery Script",
            "# Generated on: " + datetime.now().isoformat(),
            "# This script will recover files based on SnapTidy operation logs",
            "",
            "import os",
            "import shutil",
            "from pathlib import Path",
            "",
            "def recover_files():",
            '    """Recover files based on SnapTidy operation logs."""',
            "    recovered_count = 0",
            "    errors = []",
            "",
            '    print("🔄 SnapTidy 복구 스크립트 시작...")',
            '    print(f"📋 총 {len(operations)} 개의 작업을 복구합니다.")',
            "",
        ]

        # Group operations by type
        operations_by_type = {}
        for op in operations:
            op_type = op["operation_type"]
            if op_type not in operations_by_type:
                operations_by_type[op_type] = []
            operations_by_type[op_type].append(op)

        # Generate recovery code for each operation type
        for op_type, ops in operations_by_type.items():
            script_lines.append(f"    # Recovering {len(ops)} {op_type} operations")

            if op_type in ["move", "copy"]:
                for op in ops:
                    source_path = op["source_path"]
                    target_path = op["target_path"]

                    if op_type == "move":
                        # For move operations, move back from target to source
                        script_lines.extend(
                            [
                                f"    try:",
                                f"        if os.path.exists('{target_path}'):",
                                f"            # Create source directory if it doesn't exist",
                                f"            os.makedirs(os.path.dirname('{source_path}'), exist_ok=True)",
                                f"            shutil.move('{target_path}', '{source_path}')",
                                f"            print(f'✅ 복구됨: {source_path}')",
                                f"            recovered_count += 1",
                                f"        else:",
                                f"            print(f'⚠️  파일 없음: {target_path}')",
                                f"    except Exception as e:",
                                f"        error_msg = f'❌ 복구 실패 {source_path}: {{e}}'",
                                f"        print(error_msg)",
                                f"        errors.append(error_msg)",
                                "",
                            ]
                        )
                    else:  # copy
                        # For copy operations, just remove the copy
                        script_lines.append(
                            f"    # Copy operation - removing copy at {target_path}"
                        )
                        script_lines.extend(
                            [
                                f"    try:",
                                f"        if os.path.exists('{target_path}'):",
                                f"            os.remove('{target_path}')",
                                f"            print(f'🗑️  복사본 제거: {target_path}')",
                                f"            recovered_count += 1",
                                f"    except Exception as e:",
                                f"        error_msg = f'❌ 복사본 제거 실패 {target_path}: {{e}}'",
                                f"        print(error_msg)",
                                f"        errors.append(error_msg)",
                                "",
                            ]
                        )

            elif op_type == "delete":
                script_lines.extend(
                    [
                        f"    # Note: {len(ops)} files were deleted and cannot be recovered",
                        f"    print(f'⚠️  삭제된 파일 {len(ops)}개는 복구할 수 없습니다:')",
                    ]
                )
                for op in ops:
                    script_lines.append(f"    #   {op['source_path']}")
                script_lines.append("")

        script_lines.extend(
            [
                '    print(f"\\n🎉 복구 완료! {recovered_count}개 파일이 복구되었습니다.")',
                "    if errors:",
                '        print(f"\\n❌ 복구 중 {len(errors)}개 오류가 발생했습니다:")',
                "        for error in errors:",
                '            print(f"  {error}")',
                "    else:",
                '        print("✅ 모든 파일이 성공적으로 복구되었습니다!")',
                "",
                "if __name__ == '__main__':",
                "    recover_files()",
            ]
        )

        return "\n".join(script_lines)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("SnapTidy")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("SnapTidy")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
