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
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from .widgets import FolderSelector, ProgressWidget, SettingsPanel
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

        self.progress_updated.emit(30, "파일 처리 중...", "")

        # Run flatten operation
        flatten.run(
            path=self.path,
            copy=copy_mode,
            output=None if output_folder == "flattened" else output_folder,
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

        self.progress_updated.emit(30, "중복 파일 검색 중...", "")

        # Run dedup operation
        dedup.run(path=self.path, sensitivity=sensitivity, threads=threads)

        self.progress_updated.emit(100, "완료!", "중복 제거가 완료되었습니다.")
        self.operation_completed.emit(True, "중복 제거가 성공적으로 완료되었습니다.")

    def run_organize(self):
        """Run organization operation."""
        self.progress_updated.emit(10, "파일 분석 중...", "")

        date_format = self.settings.get("date_format", "year")

        self.progress_updated.emit(30, "날짜별 정리 중...", "")

        # Run organize operation
        organize.run(path=self.path, date_format=date_format)

        self.progress_updated.emit(100, "완료!", "날짜별 정리가 완료되었습니다.")
        self.operation_completed.emit(True, "날짜별 정리가 성공적으로 완료되었습니다.")


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("SnapTidy - 사진 라이브러리 정리 도구")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Main content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Folder selection and settings
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)

        # Right panel - Progress and results
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)

        # Set splitter proportions
        content_splitter.setSizes([400, 400])
        main_layout.addWidget(content_splitter)

        # Action buttons
        action_buttons = self.create_action_buttons()
        main_layout.addWidget(action_buttons)

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

    def create_left_panel(self) -> QWidget:
        """Create the left panel with folder selection and settings."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Folder selector
        self.folder_selector = FolderSelector("📁 대상 폴더")
        self.folder_selector.folder_selected.connect(self.on_folder_selected)
        layout.addWidget(self.folder_selector)

        # Settings panel
        self.settings_panel = SettingsPanel()
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        layout.addWidget(self.settings_panel)

        layout.addStretch()
        return panel

    def create_right_panel(self) -> QWidget:
        """Create the right panel with progress and results."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Progress widget
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)

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

        layout.addWidget(results_group)
        layout.addStretch()

        return panel

    def create_action_buttons(self) -> QWidget:
        """Create action buttons."""
        button_panel = QWidget()
        layout = QHBoxLayout(button_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Flatten button
        self.flatten_btn = QPushButton("📁 디렉토리 평탄화")
        self.flatten_btn.setFixedHeight(50)
        self.flatten_btn.clicked.connect(lambda: self.start_operation("flatten"))
        self.flatten_btn.setStyleSheet(self.get_button_style("#3498db"))
        layout.addWidget(self.flatten_btn)

        # Dedup button
        self.dedup_btn = QPushButton("🔍 중복 제거")
        self.dedup_btn.setFixedHeight(50)
        self.dedup_btn.clicked.connect(lambda: self.start_operation("dedup"))
        self.dedup_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        layout.addWidget(self.dedup_btn)

        # Organize button
        self.organize_btn = QPushButton("📅 날짜별 정리")
        self.organize_btn.setFixedHeight(50)
        self.organize_btn.clicked.connect(lambda: self.start_operation("organize"))
        self.organize_btn.setStyleSheet(self.get_button_style("#27ae60"))
        layout.addWidget(self.organize_btn)

        layout.addStretch()

        # Exit button
        exit_btn = QPushButton("종료")
        exit_btn.setFixedSize(80, 50)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(self.get_button_style("#95a5a6"))
        layout.addWidget(exit_btn)

        return button_panel

    def get_button_style(self, color: str) -> str:
        """Get button style for given color."""
        return f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}aa;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """

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
        self.results_label.setText(f"선택된 폴더: {folder_path}")

    def on_settings_changed(self, settings: dict):
        """Handle settings changes."""
        # Update UI based on settings
        pass

    def start_operation(self, operation: str):
        """Start a SnapTidy operation."""
        folder_path = self.folder_selector.get_folder()
        if not folder_path:
            QMessageBox.warning(self, "경고", "폴더를 선택해주세요.")
            return

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "경고", "선택한 폴더가 존재하지 않습니다.")
            return

        # Get current settings
        settings = self.settings_panel.get_settings()

        # Disable buttons during operation
        self.flatten_btn.setEnabled(False)
        self.dedup_btn.setEnabled(False)
        self.organize_btn.setEnabled(False)

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

    def on_operation_completed(self, success: bool, message: str):
        """Handle operation completion."""
        # Re-enable buttons
        self.flatten_btn.setEnabled(True)
        self.dedup_btn.setEnabled(True)
        self.organize_btn.setEnabled(True)

        # Hide progress
        self.progress_widget.hide_progress()

        # Show result
        if success:
            self.results_label.setText(message)
            QMessageBox.information(self, "완료", message)
        else:
            self.results_label.setText(f"오류: {message}")
            QMessageBox.critical(
                self, "오류", f"작업 중 오류가 발생했습니다:\n{message}"
            )


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
