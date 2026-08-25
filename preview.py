from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QUrl,
    Signal,
)
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
    QVideoSink,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSizePolicy,
)


class MediaPreview(QWidget):

    position_changed = Signal(float)
    duration_changed = Signal(float)

    start_requested = Signal(float)
    end_requested = Signal(float)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.current_path = None
        self.duration = 0

        self.last_pixmap = None

        # ==================================================
        # Media player
        # ==================================================

        self.player = QMediaPlayer(self)

        self.audio = QAudioOutput(self)

        self.player.setAudioOutput(
            self.audio
        )

        self.audio.setVolume(
            1.0
        )

        # ==================================================
        # Video sink
        # ==================================================

        self.video_sink = QVideoSink(
            self
        )

        self.player.setVideoOutput(
            self.video_sink
        )

        self.video_sink.videoFrameChanged.connect(
            self.on_video_frame
        )

        # ==================================================
        # Video display
        # ==================================================

        self.video_label = QLabel()

        self.video_label.setAlignment(
            Qt.AlignCenter
        )

        self.video_label.setMinimumHeight(
            240
        )

        self.video_label.setMaximumHeight(
            450
        )

        self.video_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.video_label.setStyleSheet(
            """
            QLabel {
                background: #000000;
                border-radius: 6px;
            }
            """
        )

        self.video_label.setText(
            "No video loaded"
        )

        # ==================================================
        # Image display
        # ==================================================

        self.image_label = QLabel()

        self.image_label.setAlignment(
            Qt.AlignCenter
        )

        self.image_label.setMinimumHeight(
            240
        )

        self.image_label.setMaximumHeight(
            450
        )

        self.image_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.image_label.setStyleSheet(
            """
            QLabel {
                background: #000000;
                border-radius: 6px;
            }
            """
        )

        self.image_label.hide()

        # ==================================================
        # Time
        # ==================================================

        self.time_label = QLabel(
            "00:00.00 / 00:00.00"
        )

        self.time_label.setAlignment(
            Qt.AlignCenter
        )

        self.time_label.setObjectName(
            "previewTime"
        )

        # ==================================================
        # Timeline
        # ==================================================

        self.timeline = QSlider(
            Qt.Horizontal
        )

        self.timeline.setRange(
            0,
            0
        )

        self.timeline.setSingleStep(
            100
        )

        self.timeline.setPageStep(
            1000
        )

        self.timeline.sliderMoved.connect(
            self.seek
        )

        # ==================================================
        # Playback controls
        # ==================================================

        controls = QHBoxLayout()

        self.start_button = QPushButton(
            "⏮"
        )

        self.start_button.setToolTip(
            "Go to start"
        )

        self.play_button = QPushButton(
            "▶"
        )

        self.play_button.setToolTip(
            "Play / Pause"
        )

        self.end_button = QPushButton(
            "⏭"
        )

        self.end_button.setToolTip(
            "Go to end"
        )

        controls.addStretch()

        controls.addWidget(
            self.start_button
        )

        controls.addWidget(
            self.play_button
        )

        controls.addWidget(
            self.end_button
        )

        controls.addStretch()

        # ==================================================
        # Range controls
        # ==================================================

        range_controls = QHBoxLayout()

        self.set_start_button = QPushButton(
            "Set Start Here"
        )

        self.set_end_button = QPushButton(
            "Set End Here"
        )

        range_controls.addWidget(
            self.set_start_button
        )

        range_controls.addWidget(
            self.set_end_button
        )

        # ==================================================
        # Layout
        # ==================================================

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            8
        )

        layout.addWidget(
            self.video_label
        )

        layout.addWidget(
            self.image_label
        )

        layout.addWidget(
            self.time_label
        )

        layout.addWidget(
            self.timeline
        )

        layout.addLayout(
            controls
        )

        layout.addLayout(
            range_controls
        )

        # ==================================================
        # Connections
        # ==================================================

        self.play_button.clicked.connect(
            self.toggle_play
        )

        self.start_button.clicked.connect(
            self.go_start
        )

        self.end_button.clicked.connect(
            self.go_end
        )

        self.player.positionChanged.connect(
            self.on_position_changed
        )

        self.player.durationChanged.connect(
            self.on_duration_changed
        )

        self.player.playbackStateChanged.connect(
            self.on_playback_state_changed
        )

        self.player.errorOccurred.connect(
            self.on_player_error
        )

        self.set_start_button.clicked.connect(
            self.set_start_here
        )

        self.set_end_button.clicked.connect(
            self.set_end_here
        )

    # ==================================================
    # Video frame received
    # ==================================================

    def on_video_frame(
        self,
        frame
    ):

        if not frame.isValid():
            return

        image = frame.toImage()

        if image.isNull():
            return

        pixmap = QPixmap.fromImage(
            image
        )

        self.last_pixmap = pixmap

        self.update_video_display()

    # ==================================================
    # Resize video while keeping aspect ratio
    # ==================================================

    def update_video_display(self):

        if self.last_pixmap is None:
            return

        target_size = (
            self.video_label.size()
        )

        if (
            target_size.width() <= 0
            or target_size.height() <= 0
        ):
            return

        scaled = self.last_pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.video_label.setPixmap(
            scaled
        )

    # ==================================================
    # Widget resize
    # ==================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        self.update_video_display()

        if (
            self.current_path
            and self.current_path.lower().endswith(
                (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".bmp",
                    ".webp",
                    ".tif",
                    ".tiff",
                )
            )
        ):

            self.update_image_display()

    # ==================================================
    # Load media
    # ==================================================

    def load_media(
        self,
        path
    ):

        self.player.stop()

        self.current_path = path

        self.last_pixmap = None

        suffix = (
            Path(path)
            .suffix
            .lower()
        )

        image_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".webp",
            ".tif",
            ".tiff",
        }

        # ==================================================
        # IMAGE
        # ==================================================

        if suffix in image_extensions:

            self.video_label.hide()

            self.image_label.show()

            pixmap = QPixmap(
                path
            )

            if not pixmap.isNull():

                self.image_label.setPixmap(
                    pixmap
                )

                self.update_image_display()

            self.timeline.setEnabled(
                False
            )

            self.play_button.setEnabled(
                False
            )

            self.start_button.setEnabled(
                False
            )

            self.end_button.setEnabled(
                False
            )

            self.set_start_button.setEnabled(
                False
            )

            self.set_end_button.setEnabled(
                False
            )

            self.time_label.setText(
                "Still Image"
            )

            return

        # ==================================================
        # VIDEO
        # ==================================================

        self.image_label.hide()

        self.video_label.show()

        self.video_label.clear()

        self.video_label.setText(
            "Loading video..."
        )

        self.timeline.setEnabled(
            True
        )

        self.play_button.setEnabled(
            True
        )

        self.start_button.setEnabled(
            True
        )

        self.end_button.setEnabled(
            True
        )

        self.set_start_button.setEnabled(
            True
        )

        self.set_end_button.setEnabled(
            True
        )

        self.player.setSource(
            QUrl.fromLocalFile(
                path
            )
        )

    # ==================================================
    # Image scaling
    # ==================================================

    def update_image_display(self):

        pixmap = self.image_label.pixmap()

        if pixmap is None:
            return

        if pixmap.isNull():
            return

        target_size = (
            self.image_label.size()
        )

        if (
            target_size.width() <= 0
            or target_size.height() <= 0
        ):
            return

        scaled = pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(
            scaled
        )

    # ==================================================
    # Playback
    # ==================================================

    def toggle_play(self):

        if (
            self.player.playbackState()
            == QMediaPlayer.PlayingState
        ):

            self.player.pause()

        else:

            self.player.play()

    def go_start(self):

        self.player.setPosition(
            0
        )

    def go_end(self):

        if self.duration:

            self.player.setPosition(
                self.duration
            )

    def seek(
        self,
        position
    ):

        self.player.setPosition(
            position
        )

    # ==================================================
    # Position
    # ==================================================

    def on_position_changed(
        self,
        position
    ):

        self.timeline.blockSignals(
            True
        )

        self.timeline.setValue(
            position
        )

        self.timeline.blockSignals(
            False
        )

        current = (
            position / 1000
        )

        duration = (
            self.duration / 1000
        )

        self.time_label.setText(
            f"{self.format_time(current)}"
            f" / "
            f"{self.format_time(duration)}"
        )

        self.position_changed.emit(
            current
        )

    # ==================================================
    # Duration
    # ==================================================

    def on_duration_changed(
        self,
        duration
    ):

        self.duration = duration

        self.timeline.setRange(
            0,
            duration
        )

        self.duration_changed.emit(
            duration / 1000
        )

        self.on_position_changed(
            self.player.position()
        )

    # ==================================================
    # Playback state
    # ==================================================

    def on_playback_state_changed(
        self,
        state
    ):

        if (
            state
            == QMediaPlayer.PlayingState
        ):

            self.play_button.setText(
                "⏸"
            )

        else:

            self.play_button.setText(
                "▶"
            )

    # ==================================================
    # Player error
    # ==================================================

    def on_player_error(
        self,
        error,
        error_string
    ):

        if error != QMediaPlayer.NoError:

            self.video_label.setText(
                "Unable to display video.\n\n"
                + (
                    error_string
                    or "Unknown media error."
                )
            )

    # ==================================================
    # Set start
    # ==================================================

    def set_start_here(self):

        position = (
            self.player.position()
            / 1000
        )

        self.start_requested.emit(
            position
        )


    # ==================================================
    # Set end
    # ==================================================

    def set_end_here(self):

        position = (
            self.player.position()
            / 1000
        )

        self.end_requested.emit(
            position
        )

    # ==================================================
    # Formatting
    # ==================================================

    @staticmethod
    def format_time(
        seconds
    ):

        seconds = max(
            0,
            seconds
        )

        minutes = int(
            seconds // 60
        )

        remaining = (
            seconds
            - minutes * 60
        )

        return (
            f"{minutes:02d}:"
            f"{remaining:05.2f}"
        )