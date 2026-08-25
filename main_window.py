import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QIcon,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QProgressBar,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QScrollArea,
    QSizePolicy,
)

from media import (
    is_supported,
    is_video,
    get_media_info,
    format_duration,
)

from converter import GifConverter
from preview import MediaPreview


class DropArea(QLabel):

    def __init__(self, parent):

        super().__init__(parent)

        self.parent_window = parent

        self.setAcceptDrops(True)

        self.setAlignment(
            Qt.AlignCenter
        )

        self.setText(
            "DROP AN IMAGE OR VIDEO HERE\n\n"
            "or click “Choose Media”"
        )

        self.setMinimumHeight(
            120
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.setObjectName(
            "dropArea"
        )

    def dragEnterEvent(
        self,
        event: QDragEnterEvent
    ):

        if event.mimeData().hasUrls():

            event.acceptProposedAction()

    def dropEvent(
        self,
        event: QDropEvent
    ):

        urls = (
            event.mimeData()
            .urls()
        )

        if urls:

            self.parent_window.set_media(
                urls[0].toLocalFile()
            )


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.media_path = None
        self.media_info = None

        self.converter = GifConverter()

        self.setWindowTitle(
            "FrameForge"
        )

        # --------------------------------------------------
        # Normal window size
        # --------------------------------------------------

        self.resize(
            1100,
            900
        )

        # Prevent the window from becoming ridiculously small
        self.setMinimumSize(
            700,
            600
        )

        self.setAcceptDrops(
            True
        )

        self.setup_icon()

        self.build_ui()

        self.apply_style()

        # --------------------------------------------------
        # Converter signals
        # --------------------------------------------------

        self.converter.progress_changed.connect(
            self.progress_changed
        )

        self.converter.status_changed.connect(
            self.status_changed
        )

        self.converter.finished.connect(
            self.conversion_finished
        )

    # ==================================================
    # Icon
    # ==================================================

    def setup_icon(self):

        icon = (
            Path(__file__).parent
            / "assets"
            / "FrameForge.ico"
        )

        if icon.exists():

            self.setWindowIcon(
                QIcon(
                    str(icon)
                )
            )

    # ==================================================
    # Build UI
    # ==================================================

    def build_ui(self):

        # ==================================================
        # SCROLL AREA
        #
        # This is the important part.
        #
        # The entire application lives inside the scroll
        # area instead of being forced to fit the window.
        # ==================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QScrollArea.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        # --------------------------------------------------
        # Scrollable content
        # --------------------------------------------------

        root = QWidget()

        root.setObjectName(
            "root"
        )

        root.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        scroll.setWidget(
            root
        )

        self.setCentralWidget(
            scroll
        )

        # ==================================================
        # MAIN LAYOUT
        # ==================================================

        layout = QVBoxLayout(
            root
        )

        layout.setContentsMargins(
            28,
            22,
            28,
            28
        )

        layout.setSpacing(
            12
        )

        # ==================================================
        # HEADER
        # ==================================================

        header = QHBoxLayout()

        logo_path = (
            Path(__file__).parent
            / "assets"
            / "frameforge_icon.png"
        )

        logo = QLabel()

        if logo_path.exists():

            logo.setPixmap(
                QIcon(
                    str(logo_path)
                ).pixmap(
                    60,
                    60
                )
            )

        logo.setFixedSize(
            60,
            60
        )

        header.addWidget(
            logo
        )

        title_box = QVBoxLayout()

        title = QLabel(
            "FrameForge"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "Turn media into motion."
        )

        subtitle.setObjectName(
            "subtitle"
        )

        title_box.addWidget(
            title
        )

        title_box.addWidget(
            subtitle
        )

        header.addLayout(
            title_box
        )

        header.addStretch()

        layout.addLayout(
            header
        )

        # ==================================================
        # DROP AREA
        # ==================================================

        self.drop_area = DropArea(
            self
        )

        layout.addWidget(
            self.drop_area
        )

        # ==================================================
        # CHOOSE MEDIA
        # ==================================================

        choose = QPushButton(
            "Choose Media"
        )

        choose.setMinimumHeight(
            38
        )

        choose.clicked.connect(
            self.choose_media
        )

        layout.addWidget(
            choose
        )

        # ==================================================
        # FILE INFORMATION
        # ==================================================

        self.file_label = QLabel(
            "No media selected"
        )

        self.file_label.setObjectName(
            "fileLabel"
        )

        self.file_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.file_label
        )

        self.info_label = QLabel(
            ""
        )

        self.info_label.setObjectName(
            "infoLabel"
        )

        layout.addWidget(
            self.info_label
        )

        # ==================================================
        # PREVIEW
        # ==================================================

        preview_group = QGroupBox(
            "Preview"
        )

        preview_group.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        preview_layout = QVBoxLayout(
            preview_group
        )

        preview_layout.setContentsMargins(
            12,
            18,
            12,
            12
        )

        self.preview = MediaPreview(
            self
        )

        self.preview.start_requested.connect(
            self.set_start_from_preview
        )

        self.preview.end_requested.connect(
            self.set_end_from_preview
        )

        preview_layout.addWidget(
            self.preview
        )

        layout.addWidget(
            preview_group
        )

        # ==================================================
        # CONVERSION SETTINGS
        # ==================================================

        settings = QGroupBox(
            "Conversion Settings"
        )

        settings.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        form = QFormLayout(
            settings
        )

        form.setLabelAlignment(
            Qt.AlignLeft
        )

        form.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow
        )

        # --------------------------------------------------
        # FPS
        # --------------------------------------------------

        self.fps = QSpinBox()

        self.fps.setRange(
            1,
            60
        )

        self.fps.setValue(
            20
        )

        self.fps.setSuffix(
            " FPS"
        )

        # --------------------------------------------------
        # Width
        # --------------------------------------------------

        self.width = QSpinBox()

        self.width.setRange(
            0,
            3840
        )

        self.width.setValue(
            640
        )

        self.width.setSpecialValueText(
            "Original"
        )

        # --------------------------------------------------
        # Height
        # --------------------------------------------------

        self.height = QSpinBox()

        self.height.setRange(
            0,
            2160
        )

        self.height.setValue(
            0
        )

        self.height.setSpecialValueText(
            "Auto"
        )

        # --------------------------------------------------
        # Start
        # --------------------------------------------------

        self.start = QDoubleSpinBox()

        self.start.setRange(
            0,
            999999
        )

        self.start.setDecimals(
            2
        )

        self.start.setSuffix(
            " s"
        )

        # --------------------------------------------------
        # End
        # --------------------------------------------------

        self.end = QDoubleSpinBox()

        self.end.setRange(
            0,
            999999
        )

        self.end.setDecimals(
            2
        )

        self.end.setSuffix(
            " s"
        )

        # --------------------------------------------------
        # Quality
        # --------------------------------------------------

        self.quality = QComboBox()

        self.quality.addItems([
            "Small File",
            "Balanced",
            "High Quality",
        ])

        self.quality.setCurrentIndex(
            1
        )

        # --------------------------------------------------
        # Loop
        # --------------------------------------------------

        self.loop = QComboBox()

        self.loop.addItems([
            "Forever",
            "Once",
        ])

        # --------------------------------------------------
        # Form
        # --------------------------------------------------

        form.addRow(
            "Frame rate:",
            self.fps
        )

        form.addRow(
            "Width:",
            self.width
        )

        form.addRow(
            "Height:",
            self.height
        )

        form.addRow(
            "Start:",
            self.start
        )

        form.addRow(
            "End:",
            self.end
        )

        form.addRow(
            "Quality:",
            self.quality
        )

        form.addRow(
            "Loop:",
            self.loop
        )

        layout.addWidget(
            settings
        )

        # ==================================================
        # OUTPUT
        # ==================================================

        output_row = QHBoxLayout()

        self.output = QLineEdit()

        self.output.setPlaceholderText(
            "Output GIF path..."
        )

        browse = QPushButton(
            "Browse"
        )

        browse.setMinimumWidth(
            90
        )

        browse.clicked.connect(
            self.choose_output
        )

        output_row.addWidget(
            self.output,
            1
        )

        output_row.addWidget(
            browse,
            0
        )

        layout.addLayout(
            output_row
        )

        # ==================================================
        # BUTTONS
        # ==================================================

        buttons = QHBoxLayout()

        self.convert_button = QPushButton(
            "Convert to GIF"
        )

        self.convert_button.setObjectName(
            "convertButton"
        )

        self.convert_button.setMinimumHeight(
            42
        )

        self.convert_button.clicked.connect(
            self.convert
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setMinimumHeight(
            42
        )

        self.cancel_button.setEnabled(
            False
        )

        self.cancel_button.clicked.connect(
            self.cancel
        )

        buttons.addWidget(
            self.convert_button,
            1
        )

        buttons.addWidget(
            self.cancel_button,
            1
        )

        layout.addLayout(
            buttons
        )

        # ==================================================
        # PROGRESS
        # ==================================================

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        layout.addWidget(
            self.progress
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status = QLabel(
            "Ready"
        )

        self.status.setObjectName(
            "status"
        )

        self.status.setWordWrap(
            True
        )

        layout.addWidget(
            self.status
        )

        # ==================================================
        # Bottom spacing
        # ==================================================

        layout.addSpacing(
            10
        )

    # ==================================================
    # Styling
    # ==================================================

    def apply_style(self):

        self.setStyleSheet(
            """

            QMainWindow,
            QWidget {
                background: #111318;
                color: #eeeeee;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QScrollArea {
                background: #111318;
                border: none;
            }

            QScrollBar:vertical {
                background: #151820;
                width: 12px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #353b48;
                border-radius: 6px;
                min-height: 35px;
            }

            QScrollBar::handle:vertical:hover {
                background: #4a5263;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar:horizontal {
                background: #151820;
                height: 12px;
            }

            QScrollBar::handle:horizontal {
                background: #353b48;
                border-radius: 6px;
                min-width: 35px;
            }

            QLabel#title {
                font-size: 32px;
                font-weight: 700;
            }

            QLabel#subtitle {
                color: #9da4b0;
                font-size: 15px;
            }

            QLabel#fileLabel {
                color: #d6dae2;
                font-weight: 600;
            }

            QLabel#infoLabel,
            QLabel#status {
                color: #9da4b0;
            }

            QLabel#dropArea {
                border: 2px dashed #4e5665;
                border-radius: 14px;
                color: #aeb5c1;
                background: #171a21;
                font-size: 16px;
                padding: 18px;
            }

            QLabel#dropArea:hover {
                border-color: #7f8cff;
                background: #1a1e27;
            }

            QGroupBox {
                border: 1px solid #303541;
                border-radius: 10px;
                margin-top: 10px;
                padding: 12px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #cbd1dc;
            }

            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QComboBox {
                background: #1a1e26;
                border: 1px solid #353b48;
                border-radius: 7px;
                padding: 7px;
                color: #eeeeee;
                min-height: 20px;
            }

            QLineEdit:focus,
            QSpinBox:focus,
            QDoubleSpinBox:focus,
            QComboBox:focus {
                border-color: #5865f2;
            }

            QPushButton {
                background: #242936;
                border: 1px solid #3a4150;
                border-radius: 8px;
                padding: 9px 15px;
            }

            QPushButton:hover {
                background: #303746;
            }

            QPushButton#convertButton {
                background: #5865f2;
                border: none;
                font-weight: 700;
            }

            QPushButton#convertButton:hover {
                background: #6975ff;
            }

            QPushButton:disabled {
                color: #6f7580;
                background: #1b1e24;
            }

            QSlider::groove:horizontal {
                height: 6px;
                background: #303541;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                width: 16px;
                margin: -5px 0;
                background: #5865f2;
                border-radius: 8px;
            }

            QProgressBar {
                border: 1px solid #343a46;
                border-radius: 7px;
                background: #181b21;
                text-align: center;
                height: 20px;
            }

            QProgressBar::chunk {
                background: #5865f2;
                border-radius: 6px;
            }

            """
        )

    # ==================================================
    # Choose Media
    # ==================================================

    def choose_media(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Media",
            "",
            "Media (*.mp4 *.mkv *.mov *.avi *.webm "
            "*.m4v *.flv *.wmv *.png *.jpg *.jpeg "
            "*.bmp *.webp *.tif *.tiff);;"
            "All Files (*)"
        )

        if path:

            self.set_media(
                path
            )

    # ==================================================
    # Set Media
    # ==================================================

    def set_media(self, path):

        if not is_supported(path):

            QMessageBox.warning(
                self,
                "Unsupported File",
                "FrameForge doesn't support "
                "that file type."
            )

            return

        self.media_path = path

        self.file_label.setText(
            f"Selected: {Path(path).name}"
        )

        self.output.setText(
            str(
                Path(path).with_suffix(
                    ".gif"
                )
            )
        )

        # --------------------------------------------------
        # Load preview
        # --------------------------------------------------

        self.preview.load_media(
            path
        )

        # --------------------------------------------------
        # Probe media
        # --------------------------------------------------

        try:

            self.media_info = (
                get_media_info(path)
            )

        except Exception as error:

            self.media_info = None

            QMessageBox.warning(
                self,
                "Media Information",
                "Could not read media information:\n\n"
                f"{error}"
            )

            return

        width = (
            self.media_info["width"]
            or "?"
        )

        height = (
            self.media_info["height"]
            or "?"
        )

        fps = (
            self.media_info["fps"]
        )

        duration = (
            self.media_info["duration"]
        )

        fps_text = (
            f"{fps:.2f} FPS"
            if fps
            else "Unknown FPS"
        )

        duration_text = (
            format_duration(
                duration
            )
        )

        self.info_label.setText(
            f"{width} × {height}  •  "
            f"{fps_text}  •  "
            f"{duration_text}"
        )

        # --------------------------------------------------
        # Video range
        # --------------------------------------------------

        if is_video(path):

            if duration:

                self.end.setRange(
                    0,
                    duration
                )

                self.end.setValue(
                    duration
                )

            else:

                self.end.setValue(
                    0
                )

        else:

            self.start.setValue(
                0
            )

            self.end.setValue(
                0
            )

        self.status.setText(
            "Media ready."
        )

    # ==================================================
    # Preview -> Start
    # ==================================================

    def set_start_from_preview(
        self,
        seconds
    ):

        self.start.setValue(
            seconds
        )

        self.status.setText(
            f"Start set to "
            f"{seconds:.2f} seconds."
        )

    # ==================================================
    # Preview -> End
    # ==================================================

    def set_end_from_preview(
        self,
        seconds
    ):

        if (
            self.media_info
            and self.media_info["duration"]
            and seconds > 0
        ):

            if seconds <= self.start.value():

                QMessageBox.warning(
                    self,
                    "Invalid End",
                    "End time must be after "
                    "the start time."
                )

                return

        self.end.setValue(
            seconds
        )

        self.status.setText(
            f"End set to "
            f"{seconds:.2f} seconds."
        )

    # ==================================================
    # Choose Output
    # ==================================================

    def choose_output(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save GIF",
            self.output.text()
            or "output.gif",
            "GIF files (*.gif)"
        )

        if path:

            if not path.lower().endswith(
                ".gif"
            ):

                path += ".gif"

            self.output.setText(
                path
            )

    # ==================================================
    # Convert
    # ==================================================

    def convert(self):

        if not self.media_path:

            QMessageBox.warning(
                self,
                "No Media",
                "Choose an image or video first."
            )

            return

        output = (
            self.output.text().strip()
        )

        if not output:

            QMessageBox.warning(
                self,
                "No Output",
                "Choose an output GIF location."
            )

            return

        start = (
            self.start.value()
        )

        end = (
            self.end.value()
        )

        if is_video(
            self.media_path
        ):

            if (
                end > 0
                and end <= start
            ):

                QMessageBox.warning(
                    self,
                    "Invalid Range",
                    "The end time must be "
                    "greater than the start time."
                )

                return

        self.convert_button.setEnabled(
            False
        )

        self.cancel_button.setEnabled(
            True
        )

        self.progress.setValue(
            0
        )

        loop_forever = (
            self.loop.currentText()
            == "Forever"
        )

        self.converter.start(
            self.media_path,
            output,
            fps=self.fps.value(),
            width=self.width.value(),
            height=self.height.value(),
            start=start,
            end=end,
            loop_forever=loop_forever,
        )

    # ==================================================
    # Progress
    # ==================================================

    def progress_changed(
        self,
        value
    ):

        self.progress.setValue(
            value
        )

    def status_changed(
        self,
        text
    ):

        self.status.setText(
            text
        )

    # ==================================================
    # Finished
    # ==================================================

    def conversion_finished(
        self,
        success,
        message
    ):

        self.convert_button.setEnabled(
            True
        )

        self.cancel_button.setEnabled(
            False
        )

        if success:

            self.progress.setValue(
                100
            )

            QMessageBox.information(
                self,
                "FrameForge",
                "GIF created successfully!\n\n"
                f"{message}"
            )

        else:

            QMessageBox.critical(
                self,
                "Conversion Failed",
                message
            )

    # ==================================================
    # Cancel
    # ==================================================

    def cancel(self):

        self.converter.cancel()

        self.convert_button.setEnabled(
            True
        )

        self.cancel_button.setEnabled(
            False
        )


# ======================================================
# Main
# ======================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "FrameForge"
    )

    app.setApplicationDisplayName(
        "FrameForge"
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()